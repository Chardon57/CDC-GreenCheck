import { BrowserRouter, Routes, Route } from 'react-router'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import './App.css'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/connexion"  element={<LoginPage />} />
        <Route path="/inscription" element={<RegisterPage />} />
        {/* Redirection par défaut vers /connexion */}
        <Route path="*" element={<LoginPage />} />
      </Routes>
    </BrowserRouter>
  )
}
