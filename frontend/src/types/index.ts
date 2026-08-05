// ============================================================
// Types partagés de l'application GreenCheck
// ============================================================

export interface User {
  id: number
  prenom: string
  nom: string
  email: string
}

export type EtatDiagnostic = 'Sain' | 'Attention' | 'Malade'

export interface Analyse {
  id: number
  date: string           // ISO 8601 : "2026-06-22T14:32:00"
  plante: string         // nom vernaculaire
  nomScientifique: string
  famille: string
  description: string
  etat: EtatDiagnostic
  niveauConfiance: number  // 0 à 100
  exposition: 'Soleil' | 'Mi-ombre' | 'Ombre'
  lieu: 'Intérieur' | 'Extérieur'
  typeCulture: 'En pot' | 'Pleine terre'
  imageUrl: string
  recommandations: string[]
}

export interface LoginPayload {
  email: string
  motDePasse: string
}

export interface RegisterPayload {
  prenom: string
  nom: string
  email: string
  motDePasse: string
  confirmMotDePasse: string
}

export interface AnalysePayload {
  image: File
  typePlante?: string
  exposition?: string
  lieu?: string
  typeCulture?: string
}
