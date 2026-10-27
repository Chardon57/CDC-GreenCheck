import { BrowserRouter, Routes, Route, Navigate } from 'react-router'
import Login from './pages/Login'
import Register from './pages/Register'
import Analysis from './pages/Analysis'
import Result from './pages/Result'
import History from './pages/History'
import Profile from './pages/Profile'
import { useEffect, useState } from 'react'
import { restaurerSession, logout, EVENEMENT_SESSION_TERMINEE } from './services/api'
import type { User, Analyse } from './types'

// Composant de route protégée — redirige vers /login si non connecté
function RouteProtegee({
  user,
  children,
}: {
  user: User | null
  children: React.ReactNode
}) {
  if (!user) return <Navigate to="/login" replace />
  return <>{children}</>
}

function App() {
  const [user, setUser] = useState<User | null>(null)
  const [dernierResultat, setDernierResultat] = useState<Analyse | null>(null)
  // Tant qu'on ne sait pas si un jeton valide existe, on n'affiche rien : sinon une page protégée
  // renverrait à tort vers /login pendant la vérification.
  const [sessionVerifiee, setSessionVerifiee] = useState(false)

  // Au démarrage (et à chaque rafraîchissement de la page) : retrouver l'utilisateur connecté.
  useEffect(() => {
    restaurerSession()
      .then(setUser)
      .finally(() => setSessionVerifiee(true))
  }, [])

  // Fin de session (jeton refusé par le backend, ou bouton « Se déconnecter ») : on oublie
  // l'utilisateur ET le dernier résultat (un autre utilisateur ne doit pas le voir), ce qui
  // renvoie automatiquement vers /login via RouteProtegee.
  useEffect(() => {
    const surSessionTerminee = () => {
      setUser(null)
      setDernierResultat(null)
    }
    window.addEventListener(EVENEMENT_SESSION_TERMINEE, surSessionTerminee)
    return () => window.removeEventListener(EVENEMENT_SESSION_TERMINEE, surSessionTerminee)
  }, [])

  if (!sessionVerifiee) {
    return (
      <div className="page">
        <main className="page__main"><p className="page__sous-titre">Chargement…</p></main>
      </div>
    )
  }

  return (
    <BrowserRouter>
      <Routes>
        {/* Routes publiques */}
        <Route path="/login"      element={<Login onLoginSuccess={setUser} />} />
        <Route path="/inscription" element={<Register onLoginSuccess={setUser} />} />

        {/* Routes protégées */}
        <Route path="/analyse" element={
          <RouteProtegee user={user}>
            <Analysis onResultat={setDernierResultat} />
          </RouteProtegee>
        }/>
        <Route path="/resultat" element={
          <RouteProtegee user={user}>
            <Result analyse={dernierResultat} />
          </RouteProtegee>
        }/>
        <Route path="/historique" element={
          <RouteProtegee user={user}>
            <History onVoirResultat={setDernierResultat} />
          </RouteProtegee>
        }/>
        <Route path="/profil" element={
          <RouteProtegee user={user}>
            <Profile onLogout={logout} />
          </RouteProtegee>
        }/>

        {/* Redirection par défaut */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App