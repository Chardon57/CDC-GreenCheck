# Moteur IA de diagnostic — GreenCheck

Service indépendant (conteneur dédié) chargé de **classer l'état d'une plante à partir d'une photo**.
Le backend l'appelle ; il ne dialogue jamais avec la base de données.

- **Modèle** : SigLIP 2 base (`google/siglip2-base-patch16-224`), utilisé en **zero-shot** : aucun
  entraînement ni fine-tuning. Le modèle compare la photo à des descriptions textuelles de chacun
  des 12 diagnostics (`labels.py`).
- **Contrat** : `POST /diagnose` (image) → `{ "label": "<nom exact d'une maladie>", "confidence": 0.0–1.0 }`
- **Limites** : précision non mesurée (pas de jeu de test) ; à présenter comme un prototype validant
  l'architecture. Pistes d'amélioration : jeu de test étiqueté, évaluation, fine-tuning sur des
  photos de plantes d'appartement.

## Contenu

| Fichier | Rôle |
|---|---|
| `labels.py` | les 12 diagnostics et leurs descriptions textuelles |
| `diagnoser.py` | logique de décision (similarités, moyenne par diagnostic, softmax) — sans dépendance au modèle |
| `siglip_embedder.py` | adaptateur vers SigLIP 2 (PyTorch + Transformers) : le seul fichier qui charge le modèle |
| `app.py` | API FastAPI : `POST /diagnose`, `GET /health` |
| `config.py` | réglages (`MODEL_NAME`, `DEVICE`, `MAX_IMAGE_MB`) lus dans l'environnement |
| `requirements.txt` | dépendances du moteur (séparées de celles du backend) |
| `Dockerfile` | image du conteneur (PyTorch CPU) |
| `tests/` | tests pytest |

## Lancer le moteur en local

```bash
cd ai_engine
python3 -m venv .venv && source .venv/bin/activate
pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu   # ou la version CUDA : pip install torch==2.14.1
pip install -r requirements-dev.txt
cp .env.example .env                  # puis adapter DEVICE si besoin
uvicorn app:app --port 8001
```

Le **premier démarrage télécharge le modèle** depuis Hugging Face (environ 1,5 Go), puis il est mis en
cache. Documentation interactive : http://127.0.0.1:8001/docs

Tests : `pytest` (utilisent un faux modèle, aucun téléchargement).
