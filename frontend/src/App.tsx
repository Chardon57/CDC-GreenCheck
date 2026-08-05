import { BrowserRouter, Routes, Route, Navigate } from 'react-router'
import Login from './pages/Login'
import Register from './pages/Register'
import Analysis from './pages/Analysis'
import Result from './pages/Result'
import History from './pages/History'
import Profile from './pages/Profile'
import { useState } from 'react'
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
            <Profile onLogout={() => setUser(null)} />
          </RouteProtegee>
        }/>

        {/* Redirection par défaut */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App