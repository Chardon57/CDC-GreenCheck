// frontend/src/pages/LoginPage.tsx

import { useState } from 'react'
import { Link } from 'react-router'
import logo from '../assets/logo_greencheck.svg'
import './LoginPage.css'

export default function LoginPage() {
  const [givenName, setGivenName] = useState('')
  const [lastName, setLastName] = useState('')
  const [email, setEmail] = useState('')
  const [motDePasse, setMotDePasse] = useState('')
  const [motDePasseConfirm, setMotDePasseConfirm] = useState('')

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    if (motDePasse !== motDePasseConfirm) {
      console.warn('Les mots de passe ne correspondent pas.')
      return
    }

    // TODO : appel API Flask ici
    console.log('Inscription avec :', email)
  }

  return (
    <div className="login-page">

      <div className="login-branding">
        <img src={logo} alt="GreenCheck" className="login-branding__logo" />
      </div>

       <form className="login-card" onSubmit={handleSubmit}>
        <h1 className="login-card__title">Inscription</h1>

        <div className="form-field">
          <label htmlFor="givenName" className="form-field__label">Prénom</label>
          <input
            id="givenName"
            className="form-field__input"
            placeholder="John"
            value={givenName}
            onChange={(e) => setGivenName(e.target.value)}
            autoComplete="given-name"
          />
        </div>

        <div className="form-field">
          <label htmlFor="lastName" className="form-field__label">Nom</label>
          <input
            id="lastName"
            className="form-field__input"
            placeholder="Smith"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            autoComplete="family-name"
          />
        </div>

        <div className="form-field">
          <label htmlFor="email" className="form-field__label">Adresse e-mail</label>
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

        <div className="form-field">
          <label htmlFor="motdepasse" className="form-field__label">Mot de passe</label>
          <input
            id="motdepasse"
            type="password"
            className="form-field__input"
            placeholder="••••••••"
            value={motDePasse}
            onChange={(e) => setMotDePasse(e.target.value)}
            autoComplete="new-password"
          />
        </div>

        <div className="form-field">
          <label htmlFor="motdepasse-confirm" className="form-field__label">
            Confirmez le mot de passe
          </label>
          <input
            id="motdepasse-confirm"
            type="password"
            className="form-field__input"
            placeholder="••••••••"
            value={motDePasseConfirm}
            onChange={(e) => setMotDePasseConfirm(e.target.value)}
            autoComplete="new-password"
          />
        </div>

        <button type="submit" className="btn btn--primary btn--full">
          S'inscrire
        </button>

        <div className="divider">
          <span className="divider__line" />
          <span className="divider__text">ou</span>
          <span className="divider__line" />
        </div>

        <div className="centered-text">
          <p className="secondary-text">Déjà un compte ?</p>
          <Link to="/connexion" className="link">Se connecter</Link>
        </div>
      </form>
    </div>
  )
}