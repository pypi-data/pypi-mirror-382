from functools import lru_cache

import numpy as np
import torch
import torch.nn.functional as F  # noqa: N812
from numpy.typing import NDArray
from PIL.Image import Image
from transformers import CLIPModel, CLIPProcessor, PreTrainedModel

from media_analyzer.machine_learning.embedding.embedder_protocol import EmbedderProtocol


@lru_cache
def get_model_and_processor() -> tuple[PreTrainedModel, CLIPProcessor]:
    """Retrieve and cache the CLIP model and processor.

    Returns:
        A tuple containing the CLIP model and CLIPProcessor.
    """
    model = CLIPModel.from_pretrained("zer0int/CLIP-GmP-ViT-L-14")
    processor = CLIPProcessor.from_pretrained("zer0int/CLIP-GmP-ViT-L-14")
    assert isinstance(processor, CLIPProcessor)
    return model, processor


class ZeroCLIPEmbedder(EmbedderProtocol):
    """Embedder implementation using the CLIP model."""

    def embed_text(self, text: str) -> NDArray[np.float32]:
        """Embed the given text.

        Args:
            text: The text to embed.

        Returns:
            The text embedding.
        """
        result: NDArray[np.float32] = self.embed_texts([text])[0]
        return result

    def embed_texts(self, texts: list[str]) -> NDArray[np.float32]:
        """Embed the given texts.

        Args:
            texts: The texts to embed.

        Returns:
            The text embeddings.
        """
        model, processor = get_model_and_processor()
        inputs_text = processor(text=texts, return_tensors="pt", padding=True)
        with torch.no_grad():
            text_embedding = model.get_text_features(**inputs_text)  # type: ignore[operator]
        return F.normalize(text_embedding, p=2, dim=-1).numpy()

    def embed_image(self, image: Image) -> NDArray[np.float32]:
        """Embed the given image.

        Args:
            image: The images to embed.

        Returns:
            The image embeddings.
        """
        result: NDArray[np.float32] = self.embed_images([image])[0]
        return result

    def embed_images(self, images: list[Image]) -> NDArray[np.float32]:
        """Embed the given images.

        Args:
            images: The images to embed.

        Returns:
            The image embeddings.
        """
        model, processor = get_model_and_processor()
        inputs_image = processor(images=images, return_tensors="pt", padding=True)
        with torch.no_grad():
            text_embedding = model.get_image_features(**inputs_image)  # type: ignore[operator]
        return F.normalize(text_embedding, p=2, dim=-1).numpy()
