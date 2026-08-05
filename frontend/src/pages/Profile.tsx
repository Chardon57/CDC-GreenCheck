import { useState, useEffect } from 'react'
import Header from '../components/Header'
import EyeIcon from '../assets/eye.svg?react'
import { getUser, updateUser, deleteUser } from '../services/api'
import type { User } from '../types'
import './pages.css'
import './Profile.css'
import { useNavigate } from 'react-router'
import TitrePage from '../components/TitrePage'

interface ProfileProps {
  onLogout: () => void
}

function Profile({ onLogout }: ProfileProps) {
  const [user, setUser] = useState<User | null>(null)
  const [prenom, setPrenom] = useState('')
  const [nom, setNom] = useState('')
  const [email, setEmail] = useState('')
  const [mdpActuel, setMdpActuel] = useState('')
  const [nouveauMdp, setNouveauMdp] = useState('')
  const [confirmMdp, setConfirmMdp] = useState('')
  const [afficherMdp, setAfficherMdp] = useState(false)
  const [messageSucces, setMessageSucces] = useState('')
  const [erreur, setErreur] = useState('')
  const [chargement, setChargement] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    getUser().then((u) => {
      setUser(u)
      setPrenom(u.prenom)
      setNom(u.nom)
      setEmail(u.email)
    })
  }, [])

  const handleEnregistrer = async (e: React.FormEvent) => {
    e.preventDefault()
    if (nouveauMdp && nouveauMdp !== confirmMdp) {
      setErreur('Les mots de passe ne correspondent pas.')
      return
    }
    setErreur('')
    setChargement(true)
    try {
      const updated = await updateUser({ prenom, nom, email })
      setUser(updated)
      setMessageSucces('Profil mis à jour.')
      setTimeout(() => setMessageSucces(''), 3000)
    } catch {
      setErreur('Erreur lors de la mise à jour.')
    } finally {
      setChargement(false)
    }
  }

  const handleSupprimerCompte = async () => {
    if (!window.confirm('Supprimer définitivement votre compte ? Cette action est irréversible.')) return
    await deleteUser()
    onLogout()
    navigate('/login')
  }

  if (!user) {
    return (
      <div className="page">
        <TitrePage titre='Profile' />
        <Header />
        <main className="page__main"><p className="page__sous-titre">Chargement…</p></main>
      </div>
    )
  }

  const champsMotDePasse = [
    { id: 'mdp-actuel', label: 'Mot de passe actuel', val: mdpActuel, set: setMdpActuel },
    { id: 'mdp-nouveau', label: 'Nouveau mot de passe', val: nouveauMdp, set: setNouveauMdp },
    { id: 'mdp-confirm', label: 'Confirmer le nouveau mot de passe', val: confirmMdp, set: setConfirmMdp },
  ]

  return (
    <div className="page">
      <TitrePage titre='Profil' />
      <Header />

      <main className="page__main profile-main">
        <h1 className="page__titre">Mon profil</h1>

        <form onSubmit={handleEnregistrer} noValidate>

          {/* Informations personnelles */}
          <section className="profile-section">
            <h2 className="profile-section__titre">Informations personnelles</h2>
            <div className="profile-card">
              {[
                { id: 'prenom', label: 'Prénom', val: prenom, set: setPrenom, type: 'text' },
                { id: 'nom', label: 'Nom', val: nom, set: setNom, type: 'text' },
                { id: 'email', label: 'Adresse e-mail', val: email, set: setEmail, type: 'email' },
              ].map(({ id, label, val, set, type }, i, arr) => (
                <div key={id} className={i === arr.length - 1 ? 'profile-field profile-field--last' : 'profile-field'}>
                  <label htmlFor={id} className="profile-field__label">{label}</label>
                  <input
                    id={id}
                    type={type}
                    className="profile-field__input"
                    value={val}
                    onChange={(e) => set(e.target.value)}
                  />
                </div>
              ))}
            </div>
          </section>

          {/* Mot de passe */}
          <section className="profile-section">
            <h2 className="profile-section__titre">Mot de passe</h2>
            <div className="profile-card">
              {champsMotDePasse.map(({ id, label, val, set }, i, arr) => (
                <div key={id} className={i === arr.length - 1 ? 'profile-field profile-field--last' : 'profile-field'}>
                  <label htmlFor={id} className="profile-field__label">{label}</label>
                  <div className="form-group__input-wrap">
                    <input
                      id={id}
                      type={afficherMdp ? 'text' : 'password'}
                      className="profile-field__input profile-field__input--password"
                      value={val}
                      onChange={(e) => set(e.target.value)}
                    />
                    <button
                      type="button"
                      className="form-group__eye-btn"
                      onClick={() => setAfficherMdp(!afficherMdp)}
                      aria-label="Afficher/masquer"
                    >
                      <EyeIcon />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {erreur && <p className="msg-erreur">{erreur}</p>}
          {messageSucces && <p className="msg-succes">{messageSucces}</p>}

          <button type="submit" className="btn btn--primary btn--full" disabled={chargement}>
            {chargement ? 'Enregistrement…' : 'Enregistrer'}
          </button>
        </form>

        <hr className="separateur" />

        <section className="profile-danger">
          <h2 className="profile-danger__titre">Suppression du compte</h2>
          <p className="profile-danger__avertissement">Attention, cette action est irréversible.</p>
          <button className="btn btn--danger btn--full" onClick={handleSupprimerCompte}>
            Supprimer mon compte
          </button>
        </section>
      </main>
    </div>
  )
}

export default Profile
