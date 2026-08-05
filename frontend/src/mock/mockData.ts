// ============================================================
// DONNÉES MOCK — Déconnecter quand le backend Flask est prêt
//
// Pour basculer sur l'API réelle :
//   Dans src/services/api.ts, passer USE_MOCK à false
// ============================================================

import type { User, Analyse } from '../types'

export const MOCK_USER: User = {
  id: 1,
  prenom: 'Jean-Patrick',
  nom: 'Glad',
  email: 'jp.glad@example.com',
}

export const MOCK_ANALYSES: Analyse[] = [
  {
    id: 1,
    date: '2026-06-22T14:32:00',
    plante: 'Saintpaulia',
    nomScientifique: 'Saintpaulia ionantha',
    famille: 'Gesnériacées',
    description:
      "Plante d'intérieur compacte, appréciée pour ses fleurs colorées. Sensible à l'excès d'eau et aux courants d'air.",
    etat: 'Sain',
    niveauConfiance: 87,
    exposition: 'Soleil',
    lieu: 'Intérieur',
    typeCulture: 'En pot',
    imageUrl: 'https://upload.wikimedia.org/wikipedia/commons/a/a0/Saintpaulia_ionantha.jpg?utm_source=commons.wikimedia.org&utm_campaign=index&utm_content=original',
    recommandations: [
      'Arroser modérément, laisser sécher entre deux arrosages',
      'Éviter la lumière directe du soleil, privilégier la lumière indirecte',
      'Maintenir une température entre 18°C et 24°C',
    ],
  },
  {
    id: 2,
    date: '2026-06-18T09:15:00',
    plante: 'Monstera',
    nomScientifique: 'Monstera deliciosa',
    famille: 'Aracées',
    description:
      "Grande plante tropicale aux feuilles découpées caractéristiques. Très populaire en décoration d'intérieur.",
    etat: 'Attention',
    niveauConfiance: 74,
    exposition: 'Mi-ombre',
    lieu: 'Intérieur',
    typeCulture: 'En pot',
    imageUrl: 'https://upload.wikimedia.org/wikipedia/commons/7/79/Monstera_deliciosa_4.jpg?utm_source=commons.wikimedia.org&utm_campaign=index&utm_content=original',
    recommandations: [
      'Vérifier le drainage, éviter les excès d\'eau',
      'Augmenter l\'humidité ambiante',
      'Nettoyer les feuilles pour favoriser la photosynthèse',
    ],
  },
  {
    id: 3,
    date: '2026-06-12T16:45:00',
    plante: 'Ficus',
    nomScientifique: 'Ficus benjamina',
    famille: 'Moracées',
    description:
      'Arbre décoratif sensible aux changements d\'environnement. Perd ses feuilles au moindre stress.',
    etat: 'Malade',
    niveauConfiance: 91,
    exposition: 'Mi-ombre',
    lieu: 'Intérieur',
    typeCulture: 'En pot',
    imageUrl: 'https://upload.wikimedia.org/wikipedia/commons/0/09/Ficus-benjamina.jpg?utm_source=commons.wikimedia.org&utm_campaign=index&utm_content=original',
    recommandations: [
      'Traiter avec un fongicide adapté',
      'Isoler la plante pour éviter la contamination',
      'Supprimer les feuilles atteintes',
    ],
  },
  {
    id: 4,
    date: '2026-06-05T11:00:00',
    plante: 'Pothos',
    nomScientifique: 'Epipremnum aureum',
    famille: 'Aracées',
    description:
      'Plante grimpante robuste et facile d\'entretien. Excellente pour purifier l\'air intérieur.',
    etat: 'Sain',
    niveauConfiance: 95,
    exposition: 'Mi-ombre',
    lieu: 'Intérieur',
    typeCulture: 'En pot',
    imageUrl: 'https://upload.wikimedia.org/wikipedia/commons/b/b7/Epipremnum_aureum_%28Marble_Queen%29_houseplant_%282%29.png?utm_source=commons.wikimedia.org&utm_campaign=index&utm_content=original',
    recommandations: [
      'Continuer l\'arrosage régulier sans excès',
      'Bouturer pour multiplier la plante',
    ],
  },
  {
    id: 5,
    date: '2026-05-28T10:20:00',
    plante: 'Orchidée',
    nomScientifique: 'Phalaenopsis amabilis',
    famille: 'Orchidacées',
    description:
      "L'une des orchidées les plus cultivées. Fleurs élégantes et longévité remarquable avec un entretien adapté.",
    etat: 'Sain',
    niveauConfiance: 88,
    exposition: 'Mi-ombre',
    lieu: 'Intérieur',
    typeCulture: 'En pot',
    imageUrl: 'https://upload.wikimedia.org/wikipedia/commons/d/dc/Phalaenopsis-de.jpg?utm_source=commons.wikimedia.org&utm_campaign=index&utm_content=original',
    recommandations: [
      'Arroser une fois par semaine en immergeant le pot',
      'Exposer à la lumière indirecte',
    ],
  },
]
