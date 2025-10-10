from typing import Protocol

from PIL.Image import Image


class CaptionerProtocol(Protocol):
    """Protocol for captioning images."""

    def caption(self, image: Image, instruction: str | None = None) -> str:
        """Generate a caption for the given image.

        Args:
            image: The image to caption.
            instruction: Optional instruction to prompt the caption model.
        """
