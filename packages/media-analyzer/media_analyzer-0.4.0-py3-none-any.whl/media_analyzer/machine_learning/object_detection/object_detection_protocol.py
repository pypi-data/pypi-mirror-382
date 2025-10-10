from typing import Protocol

from PIL.Image import Image

from media_analyzer.data.interfaces.ml_types import ObjectBox


class ObjectDetectionProtocol(Protocol):
    """Protocol for object detection."""

    def detect_objects(self, image: Image) -> list[ObjectBox]:
        """Check if an image has legible text."""
