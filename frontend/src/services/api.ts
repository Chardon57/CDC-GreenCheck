// ============================================================
// SERVICE API — GreenCheck
//
// Seul fichier du frontend qui parle au backend (FastAPI).
// Les pages appellent ces fonctions et n'utilisent jamais fetch() directement.
//
// MODE MOCK / API RÉELLE — choisi dans frontend/.env (puis redémarrer `pnpm dev`) :
//   VITE_USE_MOCK=false (ou absent) → vraie API
//   VITE_USE_MOCK=true              → données fictives, sans backend
//
// ÉTAT DE LA MIGRATION « MOCK → API RÉELLE » (mode réel) :
//   ✔ Authentification (login, register, getUser, logout) : branchée
//   ✘ Analyses, PDF : pas encore branchés (étapes suivantes)
//   ✘ Profil (modification, suppression du compte) : pas encore côté backend
// ============================================================

import { MOCK_USER, MOCK_ANALYSES } from '../mock/mockData'
import type { User, Analyse, LoginPayload, RegisterPayload, AnalysePayload } from '../types'

// ── Configuration ──────────────────────────────────────────
// Variable lue dans frontend/.env. Une variable d'environnement est toujours un TEXTE :
// on compare donc avec la chaîne 'true' (tout autre valeur, ou l'absence de variable, = API réelle).
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'
if (USE_MOCK) console.info('[GreenCheck] Mode MOCK actif : aucune requête n\'est envoyée au backend.')

// Adresse du backend, définie dans frontend/.env (VITE_API_URL). Le .replace retire un éventuel « / » final.
const API_BASE_URL = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace(/\/+$/, '')
// ───────────────────────────────────────────────────────────

// Délai artificiel pour simuler la latence réseau en mode mock
const mockDelay = (ms = 400) => new Promise((res) => setTimeout(res, ms))

// ── Jeton d'authentification (JWT) ──────────────────────────
// Après la connexion, le backend remet un « jeton » : une preuve d'identité valable 30 minutes.
// On le garde dans sessionStorage : il survit à un rafraîchissement de la page, mais disparaît
// à la fermeture de l'onglet. Chaque requête protégée le renvoie dans l'en-tête Authorization.
const CLE_JETON = 'greencheck_jeton'

function lireJeton(): string | null {
  try {
    return sessionStorage.getItem(CLE_JETON)
  } catch {
    return null // stockage indisponible (navigation privée stricte, par exemple)
  }
}

function memoriserJeton(jeton: string): void {
  try {
    sessionStorage.setItem(CLE_JETON, jeton)
  } catch {
    /* sans stockage, l'utilisateur devra se reconnecter à chaque rafraîchissement */
  }
}

function oublierJeton(): void {
  try {
    sessionStorage.removeItem(CLE_JETON)
  } catch {
    /* rien à faire */
  }
}

// ── Erreurs et requêtes ─────────────────────────────────────

// Erreur « maison » : en plus du message, elle porte le code HTTP (401, 409…).
// status = 0 signifie que le serveur n'a pas pu être joint du tout.
export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

// Signal envoyé à toute l'application quand la session prend fin : jeton refusé par le backend
// (expiré, invalide) ou déconnexion volontaire. App.tsx l'écoute et renvoie vers la page de connexion.
export const EVENEMENT_SESSION_TERMINEE = 'greencheck:session-terminee'

// FastAPI renvoie ses erreurs sous la forme {"detail": "message"} ; on en extrait le message.
async function lireDetail(res: Response): Promise<string> {
  try {
    const corps = await res.json()
    if (typeof corps?.detail === 'string') return corps.detail
  } catch {
    /* corps absent ou qui n'est pas du JSON */
  }
  return `Erreur ${res.status}`
}

// Point de passage unique de TOUTES les requêtes : ajoute le jeton, traduit les échecs en ApiError.
async function requete(
  chemin: string,
  options: RequestInit = {},
  avecJeton = true,
): Promise<Response> {
  const headers = new Headers(options.headers)
  const jeton = lireJeton()
  if (avecJeton && jeton) headers.set('Authorization', `Bearer ${jeton}`)

  let res: Response
  try {
    res = await fetch(`${API_BASE_URL}${chemin}`, { ...options, headers })
  } catch {
    // fetch ne « rejette » que si le réseau est coupé, le serveur éteint ou le CORS refusé
    throw new ApiError(0, 'Impossible de joindre le serveur.')
  }

  if (!res.ok) {
    if (res.status === 401 && avecJeton) {
      oublierJeton()
      window.dispatchEvent(new Event(EVENEMENT_SESSION_TERMINEE))
    }
    throw new ApiError(res.status, await lireDetail(res))
  }
  return res
}

const JSON_HEADERS = { 'Content-Type': 'application/json' }

// ── Auth ────────────────────────────────────────────────────

// Forme de l'utilisateur renvoyé par le backend (noms anglais, voir schemas/user.py)
interface UserApi {
  id_user: number
  surname: string // nom de famille
  name: string    // prénom
  email: string
}

// « Adaptateur » : traduit le vocabulaire du backend vers celui du frontend.
function versUser(u: UserApi): User {
  return { id: u.id_user, prenom: u.name, nom: u.surname, email: u.email }
}

// Mode mock : un faux jeton suffit à « rester connecté » après un rafraîchissement.
const JETON_MOCK = 'jeton-mock'
const MOCK_CREDENTIALS = { email: 'jp.glad@example.com', motDePasse: 'test1234' }

export async function login(payload: LoginPayload): Promise<User> {
  if (USE_MOCK) {
    await mockDelay()
    if (payload.email === MOCK_CREDENTIALS.email && payload.motDePasse === MOCK_CREDENTIALS.motDePasse) {
      memoriserJeton(JETON_MOCK)
      return MOCK_USER
    }
    throw new ApiError(401, 'Identifiants invalides')
  }
  // 1) échange e-mail + mot de passe contre un jeton (requête SANS jeton : on n'en a pas encore)
  const res = await requete(
    '/auth/login',
    {
      method: 'POST',
      headers: JSON_HEADERS,
      body: JSON.stringify({ email: payload.email, password: payload.motDePasse }),
    },
    false,
  )
  const { access_token } = await res.json()
  memoriserJeton(access_token)
  // 2) le jeton ne contient pas le profil : on le demande au backend
  return getUser()
}

export async function register(payload: RegisterPayload): Promise<User> {
  if (USE_MOCK) {
    await mockDelay()
    memoriserJeton(JETON_MOCK)
    return { ...MOCK_USER, prenom: payload.prenom, nom: payload.nom, email: payload.email }
  }
  await requete(
    '/auth/register',
    {
      method: 'POST',
      headers: JSON_HEADERS,
      body: JSON.stringify({
        surname: payload.nom,
        name: payload.prenom,
        email: payload.email,
        password: payload.motDePasse,
      }),
    },
    false,
  )
  // Le backend ne renvoie pas de jeton à l'inscription : on connecte l'utilisateur dans la foulée.
  return login({ email: payload.email, motDePasse: payload.motDePasse })
}

// Le jeton est « sans état » côté serveur : se déconnecter = simplement l'oublier ici,
// puis prévenir l'application (App.tsx efface l'utilisateur et renvoie vers /login).
export function logout(): void {
  oublierJeton()
  window.dispatchEvent(new Event(EVENEMENT_SESSION_TERMINEE))
}

// Au chargement de l'application : y a-t-il un jeton encore valide ? Si oui, on retrouve l'utilisateur.
export async function restaurerSession(): Promise<User | null> {
  if (!lireJeton()) return null
  if (USE_MOCK) return lireJeton() === JETON_MOCK ? MOCK_USER : null
  try {
    return await getUser()
  } catch {
    return null
  }
}

// ── Analyses ────────────────────────────────────────────────

export async function getAnalyses(): Promise<Analyse[]> {
  if (USE_MOCK) {
    await mockDelay()
    return MOCK_ANALYSES
  }
  const res = await fetch(`${API_BASE_URL}/analyses`, { credentials: 'include' })
  if (!res.ok) throw new Error('Impossible de récupérer l\'historique')
  return res.json()
}

export async function getAnalyse(id: number): Promise<Analyse> {
  if (USE_MOCK) {
    await mockDelay()
    const found = MOCK_ANALYSES.find((a) => a.id === id)
    if (!found) throw new Error('Analyse introuvable')
    return found
  }
  const res = await fetch(`${API_BASE_URL}/analyses/${id}`, { credentials: 'include' })
  if (!res.ok) throw new Error('Analyse introuvable')
  return res.json()
}

export async function deleteAnalyse(id: number): Promise<void> {
  if (USE_MOCK) { await mockDelay(200); return }
  const res = await fetch(`${API_BASE_URL}/analyses/${id}`, {
    method: 'DELETE',
    credentials: 'include',
  })
  if (!res.ok) throw new Error('Erreur lors de la suppression')
}

export async function lancerAnalyse(_payload: AnalysePayload): Promise<Analyse> {
  if (USE_MOCK) {
    await mockDelay(1500)
    return MOCK_ANALYSES[0]
  }
  const formData = new FormData()
  formData.append('image', _payload.image)
  if (_payload.typePlante) formData.append('type_plante', _payload.typePlante)
  if (_payload.exposition) formData.append('exposition', _payload.exposition)
  if (_payload.lieu) formData.append('lieu', _payload.lieu)
  if (_payload.typeCulture) formData.append('type_culture', _payload.typeCulture)
  const res = await fetch(`${API_BASE_URL}/analyses`, {
    method: 'POST',
    credentials: 'include',
    body: formData,
  })
  if (!res.ok) throw new Error('Erreur lors de l\'analyse')
  return res.json()
}

// ── Profil ──────────────────────────────────────────────────

export async function getUser(): Promise<User> {
  if (USE_MOCK) { await mockDelay(); return MOCK_USER }
  const res = await requete('/auth/me')
  return versUser(await res.json())
}

export async function updateUser(data: Partial<User>): Promise<User> {
  if (USE_MOCK) { await mockDelay(); return { ...MOCK_USER, ...data } }
  // Pas encore d'équivalent côté backend (prévu dans une étape ultérieure).
  throw new Error('La modification du profil n\'est pas encore disponible.')
}

export async function deleteUser(): Promise<void> {
  if (USE_MOCK) { await mockDelay(); return }
  throw new Error('La suppression du compte n\'est pas encore disponible.')
}

// ── Export PDF ─────────────────────────────────────────
export async function exporterPDF(analyse: import('../types').Analyse): Promise<void> {
  if (USE_MOCK) {
    // Génération frontend avec jsPDF
    const { jsPDF } = await import('jspdf')
    const doc = new jsPDF()

    const date = new Date(analyse.date).toLocaleDateString('fr-FR', {
      day: 'numeric', month: 'long', year: 'numeric',
    })

    // En-tête
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(20)
    doc.setTextColor(45, 90, 27)           // --color-foret
    doc.text('GreenCheck', 20, 20)

    doc.setFontSize(11)
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(100, 100, 100)
    doc.text('Diagnostic intelligent de plantes', 20, 28)

    // Ligne de séparation
    doc.setDrawColor(200, 200, 200)
    doc.line(20, 33, 190, 33)

    // Métadonnées
    doc.setFontSize(10)
    doc.setTextColor(80, 80, 80)
    doc.text(`Soumis le ${date}`, 20, 42)
    doc.text(
      `${analyse.plante} · ${analyse.exposition} · ${analyse.lieu} · ${analyse.typeCulture}`,
      20, 49
    )

    // Diagnostic
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(14)
    doc.setTextColor(45, 90, 27)
    doc.text('Diagnostic', 20, 62)

    doc.setFont('helvetica', 'normal')
    doc.setFontSize(12)
    doc.setTextColor(30, 30, 30)
    doc.text(`État : ${analyse.etat}`, 20, 72)
    doc.text(`Niveau de confiance : ${analyse.niveauConfiance}%`, 20, 80)

    // Fiche plante
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(14)
    doc.setTextColor(45, 90, 27)
    doc.text('Fiche plante', 20, 96)

    doc.setFont('helvetica', 'bold')
    doc.setFontSize(11)
    doc.setTextColor(30, 30, 30)
    doc.text(`${analyse.plante} (${analyse.nomScientifique})`, 20, 106)

    doc.setFont('helvetica', 'normal')
    doc.setFontSize(10)
    doc.setTextColor(80, 80, 80)
    doc.text(`Famille : ${analyse.famille}`, 20, 114)

    // Description avec retour à la ligne automatique
    const descLines = doc.splitTextToSize(analyse.description, 170)
    doc.setTextColor(30, 30, 30)
    doc.text(descLines, 20, 122)

    // Recommandations
    const yReco = 122 + descLines.length * 6 + 10
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(14)
    doc.setTextColor(45, 90, 27)
    doc.text('Recommandations', 20, yReco)

    doc.setFont('helvetica', 'normal')
    doc.setFontSize(10)
    doc.setTextColor(30, 30, 30)
    analyse.recommandations.forEach((rec, i) => {
      const lines = doc.splitTextToSize(`• ${rec}`, 165)
      doc.text(lines, 25, yReco + 10 + i * 12)
    })

    // Pied de page
    doc.setFontSize(8)
    doc.setTextColor(150, 150, 150)
    doc.text(
      `Rapport généré par GreenCheck — Analyse #${analyse.id}`,
      20, 285
    )

    // Téléchargement — déclenche la boîte de dialogue native du navigateur
    doc.save(`${analyse.id}.pdf`)
    return
  }

  // Mode réel — le backend génère et stocke le PDF
  const res = await fetch(`${API_BASE_URL}/analyses/${analyse.id}/pdf`, {
    credentials: 'include',
  })
  if (!res.ok) throw new Error('Erreur lors de la génération du PDF')
  const { url } = await res.json()   // le backend retourne { url: "/1/analyses/3.pdf" }

  // Ouvre l'URL dans un nouvel onglet : le navigateur propose Ouvrir/Enregistrer nativement
  window.open(url, '_blank')
}