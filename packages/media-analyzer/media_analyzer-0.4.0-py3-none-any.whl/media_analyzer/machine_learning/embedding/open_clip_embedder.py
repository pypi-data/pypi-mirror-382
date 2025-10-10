from functools import lru_cache

import numpy as np
import PIL.Image
import torch
import torch.nn.functional as F  # noqa: N812
from numpy.typing import NDArray
from open_clip import CLIP, SimpleTokenizer, create_model_and_transforms, get_tokenizer
from torchvision.transforms import Compose

from media_analyzer.machine_learning.embedding.embedder_protocol import EmbedderProtocol


@lru_cache
def get_open_clip_assets() -> tuple[CLIP, Compose, SimpleTokenizer, str]:
    """Retrieve and cache the OpenCLIP model, preprocessor, tokenizer, and device.

    This function ensures that the heavyweight model is only loaded from disk
    and moved to the GPU once, the first time it's called.

    Returns:
        A tuple containing the model, image preprocessor, tokenizer, and device string.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading OpenCLIP ViT-H-14 model on device: '{device}'")

    model, _, preprocess = create_model_and_transforms(
        "ViT-H-14", pretrained="laion2b_s32b_b79k", device=device
    )
    # Put the model in evaluation mode
    model.eval()

    tokenizer = get_tokenizer("ViT-H-14")

    print("Model loaded successfully.")
    return model, preprocess, tokenizer, device


class OpenCLIPEmbedder(EmbedderProtocol):
    """Embedder implementation using the OpenCLIP ViT-H-14 model."""

    def embed_text(self, text: str) -> NDArray[np.float32]:
        """Embed a single string of text.

        Args:
            text: The text to embed.

        Returns:
            A 1D NumPy array representing the text embedding.
        """
        result: NDArray[np.float32] = self.embed_texts([text])[0]
        return result

    def embed_texts(self, texts: list[str]) -> NDArray[np.float32]:
        """Embed a list of texts.

        Args:
            texts: The list of texts to embed.

        Returns:
            A 2D NumPy array of shape (n_texts, embedding_dim).
        """
        model, _, tokenizer, device = get_open_clip_assets()

        # Tokenize the text and move to the target device
        text_tokens = tokenizer(texts).to(device)

        with torch.no_grad():
            # Generate text features (embeddings)
            text_features = model.encode_text(text_tokens)
            # Normalize the features to have unit length
            text_features = F.normalize(text_features, p=2, dim=-1)

        # Move to CPU and convert to NumPy array
        return text_features.cpu().numpy()

    def embed_image(self, image: PIL.Image.Image) -> NDArray[np.float32]:
        """Embed a single PIL Image.

        Args:
            image: The PIL Image to embed.

        Returns:
            A 1D NumPy array representing the image embedding.
        """
        result: NDArray[np.float32] = self.embed_images([image])[0]
        return result

    def embed_images(self, images: list[PIL.Image.Image]) -> NDArray[np.float32]:
        """Embed a list of PIL Images.

        Args:
            images: The list of PIL Images to embed.

        Returns:
            A 2D NumPy array of shape (n_images, embedding_dim).
        """
        model, preprocess, _, device = get_open_clip_assets()

        # Preprocess each image and stack them into a single tensor
        image_tensors = torch.stack([preprocess(img) for img in images]).to(device)

        with torch.no_grad():
            # Generate image features (embeddings)
            image_features = model.encode_image(image_tensors)
            # Normalize the features to have unit length
            image_features = F.normalize(image_features, p=2, dim=-1)

        # Move to CPU and convert to NumPy array
        return image_features.cpu().numpy()
