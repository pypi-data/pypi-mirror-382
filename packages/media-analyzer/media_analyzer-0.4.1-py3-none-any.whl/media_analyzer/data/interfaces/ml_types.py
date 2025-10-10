from dataclasses import dataclass

from media_analyzer.data.enums.face_sex import FaceSex


@dataclass
class BaseBoundingBox:
    """Base class for a bounding box with position and size.

    Attributes:
        position: The position of the bounding box, proportional to the full image width and height.
        width: The width of the bounding box.
        height: The height of the bounding box.
        confidence: The confidence of the detected item (OCR/Object/Face).
    """

    # position, width, height are proportional to full image width/height
    position: tuple[float, float]
    width: float
    height: float
    confidence: float


@dataclass
class ObjectBox(BaseBoundingBox):
    """Represents an object bounding box with a label.

    Attributes:
        label: The label of the detected object.
    """

    label: str


@dataclass
class OCRBox(BaseBoundingBox):
    """Represents a bounding box for OCR with text content.

    Attributes:
        text: The recognized text within the bounding box.
    """

    text: str


@dataclass
class FaceBox(BaseBoundingBox):
    """Represents a face bounding box with facial attributes.

    Attributes:
        age: The estimated age of the person.
        sex: The gender of the person.
        mouth_left: The position of the left mouth corner.
        mouth_right: The position of the right mouth corner.
        nose_tip: The position of the nose tip.
        eye_left: The position of the left eye.
        eye_right: The position of the right eye.
        embedding: The facial embedding vector.
    """

    age: int
    sex: FaceSex
    mouth_left: tuple[float, float]
    mouth_right: tuple[float, float]
    nose_tip: tuple[float, float]
    eye_left: tuple[float, float]
    eye_right: tuple[float, float]
    embedding: list[float]
