// ============================================================
// SERVICE API — GreenCheck
//
// BASCULE MOCK / API RÉELLE :
//   Passer USE_MOCK à false quand le backend Flask est prêt.
//   L'URL de l'API est définie dans API_BASE_URL.
// ============================================================

import { MOCK_USER, MOCK_ANALYSES } from '../mock/mockData'
import type { User, Analyse, LoginPayload, RegisterPayload, AnalysePayload } from '../types'

// ── Configuration ──────────────────────────────────────────
const USE_MOCK = true                              // ← passer à false pour l'API réelle
const API_BASE_URL = 'http://localhost:5000/api'  // ← URL du backend Flask
// ───────────────────────────────────────────────────────────

// Délai artificiel pour simuler la latence réseau en mode mock
const mockDelay = (ms = 400) => new Promise((res) => setTimeout(res, ms))

// ── Auth ────────────────────────────────────────────────────

// Identifiants mockés — à supprimer quand USE_MOCK = false
const MOCK_CREDENTIALS = {
  email: 'jp.glad@example.com',
  motDePasse: 'test1234',
}

export async function login(payload: LoginPayload): Promise<User> {
  if (USE_MOCK) {
    await mockDelay()
    if (
      payload.email === MOCK_CREDENTIALS.email &&
      payload.motDePasse === MOCK_CREDENTIALS.motDePasse
    ) {
      return MOCK_USER
    }
    throw new Error('Identifiants invalides')
  }
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: payload.email, password: payload.motDePasse }),
  })
  if (!res.ok) throw new Error('Identifiants invalides')
  return res.json()
}

export async function register(payload: RegisterPayload): Promise<User> {
  if (USE_MOCK) {
    await mockDelay()
    return { ...MOCK_USER, prenom: payload.prenom, nom: payload.nom, email: payload.email }
  }
  const res = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      first_name: payload.prenom,
      last_name: payload.nom,
      email: payload.email,
      password: payload.motDePasse,
    }),
  })
  if (!res.ok) throw new Error('Erreur lors de l\'inscription')
  return res.json()
}

export async function logout(): Promise<void> {
  if (USE_MOCK) { await mockDelay(100); return }
  await fetch(`${API_BASE_URL}/auth/logout`, { method: 'POST' })
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
  const res = await fetch(`${API_BASE_URL}/user/me`, { credentials: 'include' })
  if (!res.ok) throw new Error('Impossible de récupérer le profil')
  return res.json()
}

export async function updateUser(data: Partial<User>): Promise<User> {
  if (USE_MOCK) { await mockDelay(); return { ...MOCK_USER, ...data } }
  const res = await fetch(`${API_BASE_URL}/user/me`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Erreur lors de la mise à jour')
  return res.json()
}

export async function deleteUser(): Promise<void> {
  if (USE_MOCK) { await mockDelay(); return }
  const res = await fetch(`${API_BASE_URL}/user/me`, {
    method: 'DELETE',
    credentials: 'include',
  })
  if (!res.ok) throw new Error('Erreur lors de la suppression du compte')
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