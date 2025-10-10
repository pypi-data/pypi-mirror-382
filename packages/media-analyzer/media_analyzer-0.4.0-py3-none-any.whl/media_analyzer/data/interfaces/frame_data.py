from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypedDict

from PIL.Image import Image

from media_analyzer.data.interfaces.ml_types import FaceBox, ObjectBox, OCRBox


@dataclass
class CaptionData:
    """A model to store structured information about an image."""

    default_caption: str
    main_subject: str
    is_indoor: bool
    contains_pets: bool
    is_food_or_drink: bool
    contains_vehicle: bool
    setting: str
    is_event: bool
    contains_landmarks: bool
    is_document: bool
    contains_people: bool
    is_landscape: bool | None = None
    is_cityscape: bool | None = None
    pet_type: str | None = None
    contains_animals: bool | None = None
    animal_type: str | None = None
    food_or_drink_type: str | None = None
    vehicle_type: str | None = None
    event_type: str | None = None
    landmark_name: str | None = None
    document_type: str | None = None
    people_count: int | None = None
    people_mood: str | None = None
    photo_type: str | None = None
    is_activity: bool | None = None
    activity_description: str | None = None


@dataclass
class OCRData:
    """OCR data for a frame.

    Attributes:
        has_legible_text: Whether the text is legible.
        ocr_text: The OCR text.
        document_summary: The document summary.
        ocr_boxes: The OCR boxes.
    """

    has_legible_text: bool
    ocr_text: str | None
    document_summary: str | None
    ocr_boxes: list[OCRBox]


@dataclass
class MeasuredQualityData:
    """Measured quality data for a frame.

    Attributes:
        measured_sharpness: The measured sharpness.
        measured_noise: The measured noise.
        measured_brightness: The measured brightness.
        measured_contrast: The measured contrast.
        measured_clipping: The measured clipping.
        measured_dynamic_range: The measured dynamic range.
        quality_score: The quality score.
    """

    measured_sharpness: float
    measured_noise: int
    measured_brightness: float
    measured_contrast: float
    measured_clipping: float
    measured_dynamic_range: float
    quality_score: float


class RGBChannels(TypedDict):
    """Types for channels used in ColorHistogram."""

    red: list[int]
    green: list[int]
    blue: list[int]


class ColorHistogram(TypedDict):
    """Types for histogram dict in ColorData."""

    bins: int
    channels: RGBChannels


@dataclass
class ColorData:
    """Color info, and theme generated based on image.

    Attributes:
        themes: Generated themes based of prominent colors in the image.
        prominent_colors: Prominent colors extracted from the image.
        average_hue: Average hue value in degrees.
        average_saturation: Average saturation value [0 to 100].
        average_lightness: Average lightness value [0 to 100].
    """

    themes: list[dict[str, Any]]
    prominent_colors: list[str]
    average_hue: float
    average_saturation: float
    average_lightness: float
    histogram: ColorHistogram


@dataclass
class FrameDataOutput:
    """Data for a frame.

    Attributes:
        ocr: The OCR data.
        embedding: The embedding data.
        faces: The face boxes.
        summary: The frame summary.
        caption_data: Info extracted using caption instructions.
        objects: The object boxes.
        measured_quality: The measured quality data.
    """

    ocr: OCRData | None = None
    embedding: list[float] | None = None
    faces: list[FaceBox] | None = None
    summary: str | None = None
    caption_data: CaptionData | None = None
    objects: list[ObjectBox] | None = None
    measured_quality: MeasuredQualityData | None = None
    color: ColorData | None = None


@dataclass
class FrameData:
    """Data for a frame, including an image for using during analysis."""

    image: Image
    path: Path
    ocr: OCRData | None = None
    embedding: list[float] | None = None
    faces: list[FaceBox] | None = None
    summary: str | None = None
    caption_data: CaptionData | None = None
    objects: list[ObjectBox] | None = None
    measured_quality: MeasuredQualityData | None = None
    color: ColorData | None = None
