import React, { useState } from 'react';

export default function Home() {
  // Cet état simulera si ton utilisateur est connecté ou non (true/false)
  // Plus tard, il sera alimenté par ton backend Flask via un appel API (fetch/axios)
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  return (
    <div className="min-h-screen bg-[#F4F7F5] text-[#212529] font-sans antialiased">
      
      {/* 1. BARRE DE NAVIGATION */}
      <nav className="bg-white shadow-sm border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <span className="text-2xl" role="img" aria-label="plante">🌱</span>
            <span className="font-bold text-xl text-[#1B4332] tracking-tight">GreenCheck</span>
          </div>
          
          {/* Liens d'authentification conditionnels (React State) */}
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <a href="/dashboard" className="text-sm font-medium text-[#2D6A4F] hover:text-[#1B4332]">
                  Mon Espace
                </a>
                <button 
                  onClick={() => setIsAuthenticated(false)} 
                  className="text-sm font-medium text-[#495057] hover:text-[#212529]"
                >
                  Déconnexion
                </button>
              </>
            ) : (
              <>
                <a href="/login" className="text-sm font-medium text-[#495057] hover:text-[#212529]">
                  Connexion
                </a>
                <a 
                  href="/register" 
                  className="bg-[#1B4332] text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-[#2D6A4F] transition-colors shadow-sm"
                >
                  Créer un compte
                </a>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* 2. SECTION PRINCIPALE (HERO SECTION) */}
      <header className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-24 grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
        
        {/* Colonne Gauche : Texte et Appels à l'action */}
        <div className="space-y-6 text-center md:text-left">
          <h1 className="text-4xl md:text-5xl font-extrabold text-[#1B4332] leading-tight">
            Identifiez les maladies de vos plantes en un instant.
          </h1>
          <p class="text-lg text-[#495057] max-w-md mx-auto md:mx-0">
            Prenez une photo, obtenez un diagnostic immédiat basé sur l'intelligence artificielle et recevez des conseils d'experts pour soigner vos plantes.
          </p>
          
          <div className="flex flex-col sm:flex-row justify-center md:justify-start gap-4 pt-2">
            {isAuthenticated ? (
              <a href="/analyse" className="bg-[#1B4332] text-white text-center px-8 py-3 rounded-xl font-medium hover:bg-[#2D6A4F] transition-all shadow-md">
                Analyser une plante
              </a>
            ) : (
              <>
                <a href="/register" className="bg-[#1B4332] text-white text-center px-8 py-3 rounded-xl font-medium hover:bg-[#2D6A4F] transition-all shadow-md">
                  Commencer gratuitement
                </a>
                <a href="/login" className="border border-gray-300 bg-white text-center text-[#495057] px-8 py-3 rounded-xl font-medium hover:bg-gray-50 transition-all">
                  Se connecter
                </a>
              </>
            )}
          </div>
        </div>

        {/* Colonne Droite : Visuel/Aperçu */}
        <div className="hidden md:flex justify-center">
          <div className="w-full max-w-md p-6 bg-white rounded-2xl shadow-xl border border-gray-100 relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-2 bg-[#2D6A4F]"></div>
            <div className="space-y-4 pt-2">
              <div className="h-48 bg-gray-100 rounded-xl flex items-center justify-center text-gray-400 border-2 border-dashed border-gray-200">
                <span>📸 Aperçu du scanner d'image</span>
              </div>
              <div className="space-y-2">
                <div className="h-4 bg-gray-200 rounded w-1/3"></div>
                <div className="h-3 bg-gray-100 rounded w-3/4"></div>
                <div className="h-3 bg-gray-100 rounded w-1/2"></div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* 3. SECTION "COMMENT ÇA MARCHE ?" */}
      <section className="bg-white border-t border-gray-100 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl md:text-3xl font-bold text-center text-[#1B4332] mb-12">
            Comment fonctionne GreenCheck ?
          </h2>
          
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 text-center">
            {/* Étape 1 */}
            <div className="space-y-3 p-4">
              <div className="w-12 h-12 bg-emerald-50 text-emerald-700 rounded-full flex items-center justify-center text-xl font-bold mx-auto">1</div>
              <h3 className="font-semibold text-lg text-[#1B4332]">Téléversez une photo</h3>
              <p className="text-sm text-[#495057]">Ajoutez une image de votre plante malade et précisez son contexte environnemental.</p>
            </div>

            {/* Étape 2 */}
            <div className="space-y-3 p-4">
              <div className="w-12 h-12 bg-emerald-50 text-emerald-700 rounded-full flex items-center justify-center text-xl font-bold mx-auto">2</div>
              <h3 className="font-semibold text-lg text-[#1B4332]">Analyse par l'IA</h3>
              <p class="text-sm text-[#495057]">Notre modèle de Deep Learning analyse les symptômes visuels en moins d'une seconde.</p>
            </div>

            {/* Étape 3 */}
            <div className="space-y-3 p-4">
              <div className="w-12 h-12 bg-emerald-50 text-emerald-700 rounded-full flex items-center justify-center text-xl font-bold mx-auto">3</div>
              <h3 className="font-semibold text-lg text-[#1B4332]">Soignez votre plante</h3>
              <p className="text-sm text-[#495057]">Recevez une fiche de diagnostic automatisée et des conseils pratiques pour agir.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}