#!/bin/bash

# Lancer le backend en arrière-plan
cd backend
python3 app.py &
BACKEND_PID=$!

# Revenir à la racine puis lancer le frontend
cd ../frontend
pnpm dev &
FRONTEND_PID=$!

# Fonction pour tout arrêter proprement avec Ctrl+C
cleanup() {
    echo "Arrêt des serveurs..."
    kill $BACKEND_PID $FRONTEND_PID
    exit
}
trap cleanup SIGINT SIGTERM

# Attendre que les deux processus tournent (bloque le script ici)
wait