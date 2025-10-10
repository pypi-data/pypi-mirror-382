from typing import Any

from exiftool import ExifToolHelper

from media_analyzer.data.anaylzer_config import FullAnalyzerConfig
from media_analyzer.data.interfaces.image_data import ExifData, ImageData
from media_analyzer.processing.pipeline.pipeline_module import PipelineModule


def parse_duration(duration_str: str) -> float:
    """Parse a duration string in the format 'HH:MM:SS.SSS'."""
    h, m, s = duration_str.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def structure_exiftool_dict(exiftool_dict: dict[str, Any]) -> dict[str, Any]:
    """Exiftool keys are structured as 'File:FileName'.

    This function transforms that to a nested dict.
    """
    del exiftool_dict["SourceFile"]
    del exiftool_dict["File:Directory"]
    nested_dict: dict[str, Any] = {}

    for key, value in exiftool_dict.items():
        if isinstance(value, str) and "(Binary data" in value and "use -b option" in value:
            continue  # Ignore binary data keys

        key_parts = key.split(":")

        if len(key_parts) == 1:  # pragma: no cover
            raise ValueError("Unexpected exiftool output")
        current_level = nested_dict
        for part in key_parts[:-1]:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]
        current_level[key_parts[-1]] = value

    return nested_dict


class ExifModule(PipelineModule[ImageData]):
    """Extract EXIF data from an image using exiftool."""

    def process(self, data: ImageData, _: FullAnalyzerConfig) -> None:
        """Extract EXIF data from an image."""
        with ExifToolHelper() as et:
            result = et.execute_json(str(data.path))
            exif_dict = structure_exiftool_dict(result[0])
            if (
                "Composite" not in exif_dict
                or "File" not in exif_dict
                or "ExifTool" not in exif_dict
            ):
                raise ValueError(f"Media-analyzer does not support this file {data.path}")

        if "EXIF" in exif_dict:
            alt_ref = exif_dict["EXIF"].get("GPSAltitudeRef")
            # altitude ref = 0 means above sea level
            # ref = 1 means below sea level
            # LG G4 produces ref = 1.8 for some reason when above sea level
            #   (maybe also below?)
            if alt_ref not in {0, 1, None}:
                if "GPSAltitude" in exif_dict["Composite"]:
                    exif_dict["Composite"]["GPSAltitude"] = abs(
                        exif_dict["Composite"]["GPSAltitude"],
                    )
                exif_dict["EXIF"]["GPSAltitudeRef"] = 0

        assert "ExifTool" in exif_dict
        assert "File" in exif_dict
        assert "Composite" in exif_dict
        width = exif_dict["File"].get("ImageWidth")
        height = exif_dict["File"].get("ImageHeight")
        duration: float | None = None
        if "GIF" in exif_dict:
            width = exif_dict["GIF"]["ImageWidth"]
            height = exif_dict["GIF"]["ImageHeight"]
        if "PNG" in exif_dict:
            width = exif_dict["PNG"]["ImageWidth"]
            height = exif_dict["PNG"]["ImageHeight"]
        if "QuickTime" in exif_dict:
            duration = exif_dict["QuickTime"]["Duration"]
            width = exif_dict["QuickTime"]["ImageWidth"]
            height = exif_dict["QuickTime"]["ImageHeight"]
        if "Matroska" in exif_dict:
            width = exif_dict["Matroska"]["ImageWidth"]
            height = exif_dict["Matroska"]["ImageHeight"]
            duration = parse_duration(exif_dict["Matroska"]["Duration"])

        assert width and height
        data.exif = ExifData(
            size_bytes=exif_dict["File"]["FileSize"],
            width=width,
            height=height,
            duration=duration,
            format=exif_dict["File"]["MIMEType"],
            exif_tool=exif_dict["ExifTool"],
            file=exif_dict["File"],
            exif=exif_dict.get("EXIF"),
            xmp=exif_dict.get("XMP"),
            mpf=exif_dict.get("MPF"),
            jfif=exif_dict.get("JFIF"),
            icc_profile=exif_dict.get("ICC_Profile"),
            composite=exif_dict["Composite"],
            gif=exif_dict.get("GIF"),
            png=exif_dict.get("PNG"),
            quicktime=exif_dict.get("QuickTime"),
            matroska=exif_dict.get("Matroska"),
        )
