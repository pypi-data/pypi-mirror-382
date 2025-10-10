from enum import StrEnum


class FileModule(StrEnum):
    """Enum for selecting file-based analyzer modules."""

    DATA_URL = "DataUrlModule"
    EXIF = "ExifModule"
    GPS = "GPSModule"
    TAGS = "TagsModule"
    TIME = "TimeModule"
    WEATHER = "WeatherModule"


class VisualModule(StrEnum):
    """Enum for selecting visual based analyzer modules."""

    CAPTION = "CaptionModule"
    EMBEDDING = "EmbeddingModule"
    FACES = "FacesModule"
    OBJECTS = "ObjectsModule"
    OCR = "OCRModule"
    QUALITY_DETECTION = "QualityDetectionModule"
    SUMMARY = "SummaryModule"
    COLOR = "ColorModule"


AnalyzerModule = FileModule | VisualModule


def analyzer_module(module_name: str) -> AnalyzerModule:
    """Parses a string into an AnalyzerModule (FileModule or VisualModule)."""
    try:
        return FileModule(module_name)
    except ValueError:
        pass

    try:
        return VisualModule(module_name)
    except ValueError:
        pass

    raise ValueError(f"'{module_name}' is not a valid AnalyzerModule")
