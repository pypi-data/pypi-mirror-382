from typing import Any, Protocol

from numpy.typing import NDArray
from PIL.Image import Image


class EmbedderProtocol(Protocol):
    """Embedder protocol."""

    def embed_text(self, text: str) -> NDArray[Any]:
        """Embed a text input and return a list of floats as the embedding."""

    def embed_texts(self, texts: list[str]) -> NDArray[Any]:
        """Embed a text inputs."""

    def embed_image(self, image: Image) -> NDArray[Any]:
        """Embed an image input and return a list of floats as the embedding."""

    def embed_images(self, images: list[Image]) -> NDArray[Any]:
        """Embed images."""
