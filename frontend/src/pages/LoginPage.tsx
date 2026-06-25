// frontend/src/pages/LoginPage.tsx

import { useState } from 'react'
import { Link } from 'react-router'
import logo from '../assets/logo_greencheck.svg'
import './LoginPage.css'
import Eye from '../assets/icons/eye.svg?react'
import EyeOff from '../assets/icons/eye-off.svg?react'

export default function LoginPage() {
  // États des champs du formulaire
  const [email, setEmail] = useState('')
  const [motDePasse, setMotDePasse] = useState('')

  // Gestionnaire de soumission du formulaire
  const handleSubmit = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault()
    // TODO : appel API Flask ici
    console.log('Connexion avec :', email, motDePasse)
  }

  return (
    <div className="login-page">

      {/* ============================================
          ZONE ② — Hero / Branding
          (logo SVG)
      ============================================ */}
      <div className="login-branding">
        <img src={logo} alt="GreenCheck" className="login-branding__logo"/>
      </div>

      {/* ============================================
          ZONE ③④ — Carte formulaire + actions
      ============================================ */}
      <div className="login-card">
        <h1 className="login-card__title">Connexion</h1>

        {/* --- Champ email --- */}
        <div className="form-field">
          <label htmlFor="email" className="form-field__label">
            Adresse e-mail
          </label>
          <input
            id="email"
            type="email"
            className="form-field__input"
            placeholder="exemple@email.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
          />
        </div>

        {/* --- Champ mot de passe --- */}
        <div className="form-field">
          <label htmlFor="motdepasse" className="form-field__label">
            Mot de passe
          </label>
          <input
            id="motdepasse"
            type="password"
            className="form-field__input"
            placeholder="••••••••"
            value={motDePasse}
            onChange={(e) => setMotDePasse(e.target.value)}
            autoComplete="current-password"
          />
        </div>

        {/* --- Lien mot de passe oublié --- */}
        <div className="login-card__forgot">
          <a href="/mot-de-passe-oublie" className="link">
            Mot de passe oublié ?
          </a>
        </div>

        {/* --- Bouton principal --- */}
        <button
          className="btn btn--primary btn--full"
          onClick={handleSubmit}
        >
          Se connecter
        </button>

        {/* --- Séparateur --- */}
        <div className="divider">
          <span className="divider__line" />
          <span className="divider__text">ou</span>
          <span className="divider__line" />
        </div>

        {/* --- Bouton secondaire --- */}
        <div className='centered-text'>
          <p className='secondary-text'>Pas encore de compte ?</p>
          <Link to="/inscription" className="link">S'inscrire</Link>
        </div>
      </div>
    </div>
  )
}