import json
import os
import sys
from pathlib import Path

import httpx2
from dotenv import load_dotenv

load_dotenv()

path = Path(sys.argv[1]).expanduser()
if not path.is_file():
    # repr() rend visibles les caractères invisibles (espace de largeur nulle, etc.)
    sys.exit(f"Fichier introuvable : {str(path)!r}")

with path.open("rb") as image:
    response = httpx2.post(
        "https://my-api.plantnet.org/v2/identify/all",
        params={"api-key": os.environ["PLANTNET_API_KEY"], "lang": "fr", "nb-results": 1},
        files={"images": image},
        timeout=15,
    )
print(response.status_code)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
