import { useState } from 'react'
import EyeIcon from '../assets/eye.svg?react'
import logoFull from '../assets/logo_full.svg'
import { register } from '../services/api'
import type { User } from '../types'
import './pages.css'
import './Auth.css'
import { useNavigate } from 'react-router'
import TitrePage from '../components/TitrePage'

interface RegisterProps {
  onLoginSuccess: (user: User) => void
}

function Register({ onLoginSuccess }: RegisterProps) {
  const [prenom, setPrenom] = useState('')
  const [nom, setNom] = useState('')
  const [email, setEmail] = useState('')
  const [motDePasse, setMotDePasse] = useState('')
  const [confirmMotDePasse, setConfirmMotDePasse] = useState('')
  const [afficherMdp, setAfficherMdp] = useState(false)
  const [afficherConfirm, setAfficherConfirm] = useState(false)
  const [erreur, setErreur] = useState('')
  const [chargement, setChargement] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!prenom || !nom || !email || !motDePasse || !confirmMotDePasse) {
      setErreur('Veuillez remplir tous les champs.')
      return
    }
    if (motDePasse !== confirmMotDePasse) {
      setErreur('Les mots de passe ne correspondent pas.')
      return
    }
    if (motDePasse.length < 8) {
      setErreur('Le mot de passe doit contenir au moins 8 caractères.')
      return
    }
    setErreur('')
    setChargement(true)
    try {
      const user = await register({ prenom, nom, email, motDePasse, confirmMotDePasse })
      onLoginSuccess(user)
      navigate('/analyse')
    } catch {
      setErreur("Une erreur est survenue lors de l'inscription.")
    } finally {
      setChargement(false)
    }
  }

  return (
    // auth-page--reversed : formulaire à gauche, logo à droite sur desktop
    <div className="auth-page auth-page--reversed">
      <TitrePage titre='Inscription' />
      {/* Formulaire — gauche sur desktop */}
      <div className="auth-form-side">
        <div className="auth-form-inner">
          <h1 className="auth-form__titre">S'inscrire</h1>

          <form onSubmit={handleSubmit} noValidate>
            {erreur && <p className="msg-erreur">{erreur}</p>}

            <div className="form-row-2">
              <div className="form-group">
                <label htmlFor="prenom" className="form-group__label">Prénom</label>
                <input
                  id="prenom"
                  type="text"
                  className="form-group__input"
                  placeholder="John"
                  value={prenom}
                  onChange={(e) => setPrenom(e.target.value)}
                  autoComplete="given-name"
                />
              </div>
              <div className="form-group">
                <label htmlFor="nom" className="form-group__label">Nom</label>
                <input
                  id="nom"
                  type="text"
                  className="form-group__input"
                  placeholder="Smith"
                  value={nom}
                  onChange={(e) => setNom(e.target.value)}
                  autoComplete="family-name"
                />
              </div>
            </div>

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
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  className="form-group__eye-btn"
                  onClick={() => setAfficherMdp(!afficherMdp)}
                  aria-label={afficherMdp ? 'Masquer' : 'Afficher'}
                >
                  <EyeIcon />
                </button>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="confirm" className="form-group__label">Confirmer le mot de passe</label>
              <div className="form-group__input-wrap">
                <input
                  id="confirm"
                  type={afficherConfirm ? 'text' : 'password'}
                  className="form-group__input form-group__input--with-icon"
                  placeholder="••••••••"
                  value={confirmMotDePasse}
                  onChange={(e) => setConfirmMotDePasse(e.target.value)}
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  className="form-group__eye-btn"
                  onClick={() => setAfficherConfirm(!afficherConfirm)}
                  aria-label={afficherConfirm ? 'Masquer' : 'Afficher'}
                >
                  <EyeIcon />
                </button>
              </div>
            </div>

            <button type="submit" className="btn btn--primary btn--full" disabled={chargement}>
              {chargement ? 'Inscription…' : "S'inscrire"}
            </button>
          </form>

          <div className="divider-ou">
            <span className="divider-ou__line" />
            <span className="divider-ou__text">ou</span>
            <span className="divider-ou__line" />
          </div>

          <p className="auth-form__switch">
            Déjà un compte ?{' '}
            <button className="link link--bold" onClick={() => navigate('/login')}>
              Se connecter
            </button>
          </p>
        </div>
      </div>

      <div className="auth-split__divider" />

      {/* Logo — droite sur desktop */}
      <div className="auth-brand-side">
        <img src={logoFull} alt="GreenCheck" className="auth-brand__logo" />
      </div>
    </div>
  )
}

export default Register
