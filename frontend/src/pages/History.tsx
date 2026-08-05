import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router'
import Header from '../components/Header'
import EyeIcon from '../assets/eye.svg?react'
import TrashIcon from '../assets/trash-2.svg?react'
import { getAnalyses, deleteAnalyse } from '../services/api'
import type { Analyse } from '../types'
import './pages.css'
import './History.css'
import TitrePage from '../components/TitrePage'

const PAR_PAGE = 4

const BADGE_CLASS: Record<string, string> = {
  Sain: 'badge badge--sain',
  Attention: 'badge badge--attention',
  Malade: 'badge badge--malade',
}

interface HistoryProps {
  onVoirResultat: (analyse: Analyse) => void
}

function History({ onVoirResultat }: HistoryProps) {
  const [analyses, setAnalyses] = useState<Analyse[]>([])
  const [chargement, setChargement] = useState(true)
  const [page, setPage] = useState(1)
  const navigate = useNavigate()

  useEffect(() => {
    getAnalyses()
      .then(setAnalyses)
      .finally(() => setChargement(false))
  }, [])

  const totalPages = Math.ceil(analyses.length / PAR_PAGE)
  const analysesDePage = analyses.slice((page - 1) * PAR_PAGE, page * PAR_PAGE)

  const handleSupprimer = async (id: number) => {
    if (!window.confirm('Supprimer cette analyse ?')) return
    await deleteAnalyse(id)
    setAnalyses((prev) => prev.filter((a) => a.id !== id))
  }

  const handleVoir = (analyse: Analyse) => {
    onVoirResultat(analyse)
    navigate('/resultat')
  }

  const formaterDate = (iso: string) =>
    new Date(iso).toLocaleDateString('fr-FR', {
      day: '2-digit', month: '2-digit', year: 'numeric',
    })

  if (chargement) {
    return (
      <div className="page">
        <TitrePage titre='Historique' />
        <Header />
        <main className="page__main"><p className="page__sous-titre">Chargement…</p></main>
      </div>
    )
  }

  return (
    <div className="page">
      <TitrePage titre='Historique' />
      <Header />

      <main className="page__main">
        <h1 className="page__titre">Historique</h1>
        <p className="page__sous-titre">Vos analyses précédentes</p>

        {analyses.length === 0 ? (
          <p className="page__sous-titre">Aucune analyse pour le moment.</p>
        ) : (
          <>
            {/* Tableau — desktop uniquement */}
            <div className="history-table-wrap">
              <table className="history-table">
                <thead>
                  <tr>
                    <th className="history-table__th">Photo</th>
                    <th className="history-table__th">Date</th>
                    <th className="history-table__th">Plante</th>
                    <th className="history-table__th">État</th>
                    <th className="history-table__th">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {analysesDePage.map((analyse, idx) => (
                    <tr
                      key={analyse.id}
                      className={idx % 2 === 0 ? 'history-table__tr' : 'history-table__tr history-table__tr--alt'}
                    >
                      <td className="history-table__td">
                        <img src={analyse.imageUrl} alt={analyse.plante} className="history-table__photo" />
                      </td>
                      <td className="history-table__td">{formaterDate(analyse.date)}</td>
                      <td className="history-table__td history-table__td--plante">{analyse.plante}</td>
                      <td className="history-table__td">
                        <span className={BADGE_CLASS[analyse.etat] || 'badge'}>{analyse.etat}</span>
                      </td>
                      <td className="history-table__td">
                        <div className="history-actions">
                          <button className="history-actions__btn" onClick={() => handleVoir(analyse)} aria-label="Voir">
                            <EyeIcon />
                          </button>
                          <button className="history-actions__btn history-actions__btn--danger" onClick={() => handleSupprimer(analyse.id)} aria-label="Supprimer">
                            <TrashIcon />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Cartes — mobile uniquement */}
            <div className="history-cards">
              {analysesDePage.map((analyse) => (
                <div key={analyse.id} className="history-card">
                  <div className="history-card__header">
                    <span className="history-card__date">{formaterDate(analyse.date)}</span>
                    <span className={BADGE_CLASS[analyse.etat] || 'badge'}>{analyse.etat}</span>
                    <div className="history-actions">
                      <button className="history-actions__btn" onClick={() => handleVoir(analyse)} aria-label="Voir">
                        <EyeIcon />
                      </button>
                      <button className="history-actions__btn history-actions__btn--danger" onClick={() => handleSupprimer(analyse.id)} aria-label="Supprimer">
                        <TrashIcon />
                      </button>
                    </div>
                  </div>
                  <p className="history-card__plante">{analyse.plante}</p>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="history-pagination">
                <button
                  className="history-pagination__btn"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  ← Précédent
                </button>
                <span className="history-pagination__info">Page {page} / {totalPages}</span>
                <button
                  className={page < totalPages ? 'history-pagination__btn history-pagination__btn--active' : 'history-pagination__btn'}
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                >
                  Suivant →
                </button>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}

export default History
