from typing import Protocol

from PIL.Image import Image

from media_analyzer.data.interfaces.ml_types import FaceBox


class FacialRecognitionProtocol(Protocol):
    """Protocol for facial recognition."""

    def get_faces(self, image: Image) -> list[FaceBox]:
        """Detect and embed faces from an image.

        Args:
            image: The image to get the faces from.

        Returns:
            The face boxes.
        """
