import { exporterPDF } from '../services/api'
import Header from '../components/Header'
import type { Analyse } from '../types'
import './pages.css'
import './Result.css'
import { useState } from 'react'
import { useNavigate } from 'react-router'
import TitrePage from '../components/TitrePage'

const BADGE_CLASS: Record<string, string> = {
  Sain: 'badge badge--sain',
  Attention: 'badge badge--attention',
  Malade: 'badge badge--malade',
}

interface ResultProps {
  analyse: Analyse | null
}

function Result({ analyse }: ResultProps) {
  const [exportEnCours, setExportEnCours] = useState(false)
  const [erreurExport, setErreurExport] = useState('')
  const navigate = useNavigate()
  if (!analyse) {
    return (
      <div className="page">
        <TitrePage titre='Résultat' />
        <Header />
        <main className="page__main">
          <p className="page__sous-titre">Aucun résultat à afficher.</p>
          <button className="btn btn--primary" onClick={() => navigate('/analyse')}>
            Lancer une analyse
          </button>
        </main>
      </div>
    )
  }

  const handelExportPDF = async () => {
    if (!analyse) return
    setErreurExport('')
    setExportEnCours(true)
    try {
      await exporterPDF(analyse)
    } catch {
      setErreurExport("Erreur lors de la génération du PDF")
    } finally {
      setExportEnCours(false)
    }
  }

  const date = new Date(analyse.date)
  const dateFormatee = date.toLocaleDateString('fr-FR', {
    day: 'numeric', month: 'long', year: 'numeric',
  })
  const heureFormatee = date.toLocaleTimeString('fr-FR', {
    hour: '2-digit', minute: '2-digit',
  })

  return (
    <div className="page">
      <TitrePage titre='Résultat' />
      <Header />

      <main className="page__main">
        <h1 className="page__titre">Résultat</h1>

        <div className="result-layout">

          {/* Colonne gauche */}
          <section className="result-gauche">
            <img
              src={analyse.imageUrl}
              alt={`Photo de ${analyse.plante}`}
              className="result-image"
            />
            <p className="result-meta">Soumis le {dateFormatee} à {heureFormatee}</p>
            <p className="result-meta">
              {analyse.plante} · {analyse.exposition} · {analyse.lieu} · {analyse.typeCulture}
            </p>

            <div className="result-fiche">
              <h2 className="result-fiche__titre">Fiche plante</h2>
              <p className="result-fiche__nom">{analyse.plante} ({analyse.nomScientifique})</p>
              <p className="result-fiche__famille">Famille : {analyse.famille}</p>
              <p className="result-fiche__desc">{analyse.description}</p>
            </div>
          </section>

          {/* Colonne droite */}
          <section className="result-droite">
            <h2 className="result-section__titre">Diagnostic</h2>

            <span className={BADGE_CLASS[analyse.etat] || 'badge'}>
              {analyse.etat}
            </span>

            <div className="result-confiance">
              <div className="result-confiance__header">
                <span className="result-confiance__label">Niveau de confiance</span>
                <span className="result-confiance__valeur">{analyse.niveauConfiance}%</span>
              </div>
              <meter id='confidence_level' min="0" max="100" value={analyse.niveauConfiance}></meter>
            </div>

            <h2 className="result-section__titre result-section__titre--mt">Recommandations</h2>
            <ul className="result-recommandations">
              {analyse.recommandations.map((rec, i) => (
                <li key={i} className="result-recommandations__item">{rec}</li>
              ))}
            </ul>

            <hr className="separateur" />

            {erreurExport && <p className="msg-erreur">{erreurExport}</p>}

            <button className="btn btn--outline btn--full"
              onClick={handelExportPDF}
              disabled={exportEnCours}
              >{exportEnCours? "Génération en cours ...":"Exporter en PDF"}</button>
          </section>

        </div>
      </main>
    </div>
  )
}

export default Result
