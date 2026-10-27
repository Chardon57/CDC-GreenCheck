import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router'
import MenuIcon from '../assets/menu.svg?react'
import CloseIcon from '../assets/x.svg?react'
import logoIcon from '../assets/logo_icon.svg'
import { logout } from '../services/api'
import './Header.css'


function Header() {
  const [menuOuvert, setMenuOuvert] = useState(false)
  const navigate = useNavigate() 
  const location = useLocation() 

  const handleNav = (chemin: string) => {
    setMenuOuvert(false)
    navigate(chemin)             
  }

  return (
    <header className="header">
      <button className="header__brand" onClick={() => handleNav('/analyse')}>
        <img src={logoIcon} alt="GreenCheck" className="header__logo" />
        <span className="header__title">GreenCheck</span>
      </button>

      {/* Partie droite : menu de navigation puis bouton de déconnexion */}
      <div className="header__droite">
        <nav className={menuOuvert ? 'header__nav header__nav--open' : 'header__nav'}>
          <button
            className={location.pathname === '/analyse' ? 'nav__link nav__link--active' : 'nav__link'}
            onClick={() => handleNav('/analyse')}
          >
            Analyse
          </button>
          <button
            className={location.pathname === '/historique' ? 'nav__link nav__link--active' : 'nav__link'}
            onClick={() => handleNav('/historique')}
          >
            Historique
          </button>
          <button
            className={location.pathname === '/profil' ? 'nav__link nav__link--active' : 'nav__link'}
            onClick={() => handleNav('/profil')}
          >
            Profil
          </button>
        </nav>

        <button
          className="header__hamburger"
          onClick={() => setMenuOuvert(!menuOuvert)}
          aria-label={menuOuvert ? 'Fermer le menu' : 'Ouvrir le menu'}
          aria-expanded={menuOuvert}
        >
          {menuOuvert ? <CloseIcon /> : <MenuIcon />}
        </button>

        <button
          className="header__logout"
          onClick={() => { setMenuOuvert(false); logout() }}
          aria-label="Se déconnecter"
          title="Se déconnecter"
        >
          <span className="header__logout-icone" aria-hidden="true" />
        </button>
      </div>
    </header>
  )
}

export default Header