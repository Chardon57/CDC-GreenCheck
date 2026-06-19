![](frontend/src/assets/logo_greencheck.png)

# CDC GreenCheck

Sujet de projet fil rouge pour la formation Concepteur, Développeur spécialité Intégration IA - Année 2026

## Initialisation de la BDD et création de l'utilisateur

Éxécuter le fichier ```initialise_db_and_user.sql``` dans MariaDB ou copier et coller le SQL puis l'éxécuter (**/!\ en root**)

## Préparer l'environnement

1. Copier backend/.env.example  → backend/.env  et remplir les valeurs
2. Copier frontend/.env.example → frontend/.env et remplir les valeurs
3. Lancer le conteneur MariaDB : docker compose up -d
4. Lancer le backend           : cd backend && python main.py
5. Lancer le frontend          : cd frontend && npm run dev

## Lancer le projet

1. Faire 
   ```shell
   chmod +x start.sh   # rend le script exécutable (à faire une seule fois)
   ```
2. éxécuter le script : 
   ```bash
   ./start.sh
   ```