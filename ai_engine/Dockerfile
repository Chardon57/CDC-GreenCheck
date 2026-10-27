# Image du moteur IA de diagnostic (conteneur indépendant du backend)
FROM python:3.14-slim

# Pas de fichiers .pyc, et des logs affichés immédiatement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Le modèle téléchargé est mis en cache ici (à monter en volume pour ne pas le re-télécharger)
    HF_HOME=/models

WORKDIR /app

# 1) PyTorch version CPU (index dédié, bien plus léger que la version CUDA)
RUN pip install --no-cache-dir torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu

# 2) Le reste des dépendances (copié avant le code pour profiter du cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Le code
COPY . .

# On n'exécute pas le serveur en root
RUN useradd --create-home appuser && mkdir -p /models && chown -R appuser /models /app
USER appuser

EXPOSE 8001

# Le premier démarrage télécharge le modèle : on laisse du temps avant de juger le conteneur « unhealthy »
HEALTHCHECK --interval=30s --timeout=5s --start-period=180s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')"
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
