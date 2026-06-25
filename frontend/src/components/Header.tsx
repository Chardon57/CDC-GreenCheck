// frontend/src/components/Header.tsx

import { useState } from 'react'
import MenuIcon from '../assets/menu.svg?react'
import CloseIcon from '../assets/x.svg?react'
import logo from '../assets/logo_greencheck.png'
import './Header.css'

// Déclaration TypeScript des props acceptées par ce composant
interface HeaderProps {
  activePage: 'login' | 'register' | 'analysis' | 'result' | 'history' | 'profile'
}

export default function Header({ activePage }: HeaderProps) {
  const [menuOuvert, setMenuOuvert] = useState(false)

  return (
    <header className="header">

      {/* Zone gauche : logo + nom de l'appli */}
      <div className="header__brand">
        <img src={logo} alt="GreenCheck" className="header__logo" />
        <span className="header__title">GreenCheck</span>
      </div>

      {/* Bouton hamburger — visible uniquement sur mobile via CSS */}
      <button
        className="header__hamburger"
        onClick={() => setMenuOuvert(!menuOuvert)}
        aria-label={menuOuvert ? 'Fermer le menu' : 'Ouvrir le menu'}
      >
        {menuOuvert ? <CloseIcon /> : <MenuIcon />}
      </button>

      {/* Navigation — sa classe change selon l'état du menu */}
      <nav className={menuOuvert ? 'header__nav header__nav--open' : 'header__nav'}>
        
          href="/analysis"
          className={activePage === 'analysis' ? 'nav__link nav__link--active' : 'nav__link'}
        >
          Analyse
        </a>
        
          href="/history"
          className={activePage === 'history' ? 'nav__link nav__link--active' : 'nav__link'}
        >
          Historique
        </a>
        
          href="/profile"
          className={activePage === 'profile' ? 'nav__link nav__link--active' : 'nav__link'}
        >
          Profil
        </a>
      </nav>

    </header>
  )
}