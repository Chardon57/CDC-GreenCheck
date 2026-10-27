"""Adaptateur entre notre code et le modèle SigLIP 2 (PyTorch + Hugging Face Transformers).

C'est le SEUL fichier qui importe torch et transformers. Les imports sont faits dans __init__
pour que les tests (qui n'utilisent pas ce fichier) n'aient pas besoin de ces bibliothèques.
"""

import logging

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# SigLIP a été entraîné avec des textes complétés à 64 « tokens » : il faut donc imposer cette
# longueur (padding="max_length"), sinon les résultats sont dégradés.
TEXT_MAX_LENGTH = 64


class SiglipEmbedder:
    def __init__(self, model_name: str, device: str = "cpu") -> None:
        import torch
        from transformers import AutoModel, AutoProcessor, AutoTokenizer

        if device.startswith("cuda") and not torch.cuda.is_available():
            logger.warning("DEVICE=%s demandé mais CUDA est indisponible : repli sur le CPU.", device)
            device = "cpu"

        logger.info("Chargement du modèle %s sur %s...", model_name, device)
        self._torch = torch
        self.device = device
        self._model = AutoModel.from_pretrained(model_name).to(device).eval()
        self._processor = AutoProcessor.from_pretrained(model_name)
        self._tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.logit_scale = float(self._model.logit_scale.exp().item())
        logger.info("Modèle chargé (logit_scale=%.2f).", self.logit_scale)

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        inputs = self._tokenizer(
            texts,
            padding="max_length",
            max_length=TEXT_MAX_LENGTH,
            truncation=True,
            return_tensors="pt",
        ).to(self.device)
        with self._torch.inference_mode():
            features = self._model.get_text_features(**inputs)
        return self._normalize(features)

    def embed_image(self, image: Image.Image) -> np.ndarray:
        inputs = self._processor(images=image, return_tensors="pt").to(self.device)
        with self._torch.inference_mode():
            features = self._model.get_image_features(**inputs)
        return self._normalize(features)[0]

    def _normalize(self, features) -> np.ndarray:
        # Selon la version de transformers, on reçoit un tenseur ou un objet qui le contient.
        tensor = getattr(features, "pooler_output", features)
        tensor = tensor / tensor.norm(p=2, dim=-1, keepdim=True)
        return tensor.float().cpu().numpy()
