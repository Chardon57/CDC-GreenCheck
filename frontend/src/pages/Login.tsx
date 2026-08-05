import { useState } from 'react'
import { useNavigate } from 'react-router'
import EyeIcon from '../assets/eye.svg?react'
import logoFull from '../assets/logo_full.svg'
import { login } from '../services/api'
import type { User } from '../types'
import './pages.css'
import './Auth.css'
import TitrePage from '../components/TitrePage'

interface LoginProps {
  onLoginSuccess: (user: User) => void
}

function Login({ onLoginSuccess }: LoginProps) {
  const [email, setEmail] = useState('')
  const [motDePasse, setMotDePasse] = useState('')
  const [afficherMdp, setAfficherMdp] = useState(false)
  const [erreur, setErreur] = useState('')
  const [chargement, setChargement] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !motDePasse) {
      setErreur('Veuillez remplir tous les champs.')
      return
    }
    setErreur('')
    setChargement(true)
    try {
      const user = await login({ email, motDePasse })
      onLoginSuccess(user)
      navigate('/analyse')
    } catch {
      setErreur('Identifiants incorrects. Veuillez réessayer.')
    } finally {
      setChargement(false)
    }
  }

  return (
    <div className="auth-page">
      <TitrePage titre='' />
      {/* Logo — gauche sur desktop, haut sur mobile */}
      <div className="auth-brand-side">
        <img src={logoFull} alt="GreenCheck" className="auth-brand__logo" />
      </div>

      <div className="auth-split__divider" />

      {/* Formulaire — droite sur desktop */}
      <div className="auth-form-side">
        <div className="auth-form-inner">
          <h1 className="auth-form__titre">Se connecter</h1>

          <form onSubmit={handleSubmit} noValidate>
            {erreur && <p className="msg-erreur">{erreur}</p>}

            <div className="form-group">
              <label htmlFor="email" className="form-group__label">Adresse e-mail</label>
              <input
                id="email"
                type="email"
                className="form-group__input"
                placeholder="exemple@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
              />
            </div>

            <div className="form-group">
              <label htmlFor="motdepasse" className="form-group__label">Mot de passe</label>
              <div className="form-group__input-wrap">
                <input
                  id="motdepasse"
                  type={afficherMdp ? 'text' : 'password'}
                  className="form-group__input form-group__input--with-icon"
                  placeholder="••••••••"
                  value={motDePasse}
                  onChange={(e) => setMotDePasse(e.target.value)}
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  className="form-group__eye-btn"
                  onClick={() => setAfficherMdp(!afficherMdp)}
                  aria-label={afficherMdp ? 'Masquer le mot de passe' : 'Afficher le mot de passe'}
                >
                  <EyeIcon />
                </button>
              </div>
            </div>

            <div className="auth-form__forgot">
              <button type="button" className="link">Mot de passe oublié ?</button>
            </div>

            <button type="submit" className="btn btn--primary btn--full" disabled={chargement}>
              {chargement ? 'Connexion…' : 'Connexion'}
            </button>
          </form>

          <div className="divider-ou">
            <span className="divider-ou__line" />
            <span className="divider-ou__text">ou</span>
            <span className="divider-ou__line" />
          </div>

          <p className="auth-form__switch">
            Pas encore de compte ?{' '}
            <button className="link link--bold" onClick={() => navigate('/inscription')}>
              S'inscrire
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login
