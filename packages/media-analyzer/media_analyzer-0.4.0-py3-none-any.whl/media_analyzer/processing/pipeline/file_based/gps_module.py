from datetime import datetime
from typing import ClassVar

import reverse_geocode

from media_analyzer.data.anaylzer_config import FullAnalyzerConfig
from media_analyzer.data.enums.analyzer_module import AnalyzerModule, FileModule
from media_analyzer.data.interfaces.image_data import GPSData, ImageData, IntermediateTimeData
from media_analyzer.data.interfaces.location_types import GeoLocation
from media_analyzer.processing.pipeline.pipeline_module import PipelineModule


class GPSModule(PipelineModule[ImageData]):
    """Extract GPS data from an image."""

    depends: ClassVar[set[AnalyzerModule]] = {FileModule.EXIF}

    def process(self, data: ImageData, _: FullAnalyzerConfig) -> None:
        """Extract GPS time and location data from an image, and reverse geocode."""
        if (
            data.exif is None
            or not data.exif.composite
            or "GPSLatitude" not in data.exif.composite
            or "GPSLongitude" not in data.exif.composite
        ):
            return

        lat = data.exif.composite["GPSLatitude"]
        lon = data.exif.composite["GPSLongitude"]
        if not lat or not lon:
            return

        alt = data.exif.composite.get("GPSAltitude")
        gps_datetime: datetime | None = None
        if "GPSDateTime" in data.exif.composite:
            for date_fmt in ["%Y:%m:%d %H:%M:%S.%fZ", "%Y:%m:%d %H:%M:%SZ"]:
                try:
                    gps_datetime = datetime.strptime(  # noqa: DTZ007
                        data.exif.composite["GPSDateTime"],
                        date_fmt,
                    )
                    if gps_datetime is not None:
                        break
                except ValueError:
                    pass

        coded = reverse_geocode.get((lat, lon))
        data.time = IntermediateTimeData(datetime_utc=gps_datetime)
        data.gps = GPSData(
            latitude=lat,
            longitude=lon,
            altitude=alt,
            location=GeoLocation(
                country=coded["country"],
                province=coded.get("state"),
                city=coded["city"],
                place_latitude=coded["latitude"],
                place_longitude=coded["longitude"],
            ),
        )
