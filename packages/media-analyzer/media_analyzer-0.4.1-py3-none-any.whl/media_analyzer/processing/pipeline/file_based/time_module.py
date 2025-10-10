import re
from datetime import datetime, timedelta, timezone
from typing import ClassVar

import pytz

from media_analyzer.data.anaylzer_config import FullAnalyzerConfig
from media_analyzer.data.enums.analyzer_module import AnalyzerModule, FileModule
from media_analyzer.data.interfaces.image_data import ImageData, TimeData
from media_analyzer.processing.pipeline.pipeline_module import (
    PipelineModule,
)
from media_analyzer.processing.process_utils import timezone_finder


def get_local_datetime(data: ImageData) -> tuple[datetime, str]:
    """Get the local datetime of an image."""

    def f1() -> tuple[datetime, str]:
        """Get the datetime from the EXIF DateTimeOriginal with OffsetTimeOriginal."""
        assert data.exif and data.exif.exif
        datetime_taken = datetime.strptime(  # noqa: DTZ007
            data.exif.exif["DateTimeOriginal"],
            "%Y:%m:%d %H:%M:%S",
        )
        offset_time = data.exif.exif["OffsetTimeOriginal"]
        hours, minutes = map(int, offset_time.split(":"))
        offset = timedelta(hours=hours, minutes=minutes)
        result = datetime_taken.replace(tzinfo=timezone(offset))
        return result, "OffsetTime"

    def f2() -> tuple[datetime, str]:
        """Get the datetime from the GPS data."""
        assert data.gps and data.time
        assert data.gps.longitude and data.gps.latitude
        tz_name = timezone_finder.timezone_at(
            lng=data.gps.longitude,
            lat=data.gps.latitude,
        )
        assert tz_name is not None
        assert data.time.datetime_utc
        datetime_utc = data.time.datetime_utc.replace(tzinfo=pytz.utc)
        result = datetime_utc.astimezone(pytz.timezone(tz_name))
        return result, "GPS"

    def f3() -> tuple[datetime, str]:
        """Get the datetime from the EXIF DateTimeOriginal."""
        assert data.exif and data.exif.exif
        result = datetime.strptime(  # noqa: DTZ007
            data.exif.exif["DateTimeOriginal"],
            "%Y:%m:%d %H:%M:%S",
        )
        return result, "DateTimeOriginal"

    def f4() -> tuple[datetime, str]:
        """Get the datetime from the EXIF CreateDate."""
        assert data.exif and data.exif.exif
        result = datetime.strptime(  # noqa: DTZ007
            data.exif.exif["CreateDate"], "%Y:%m:%d %H:%M:%S"
        )
        return result, "DateTimeOriginal"

    def f5() -> tuple[datetime, str]:
        """Get the datetime from the filename."""
        # Use a regex to find the first 8 digits (YYYYMMDD) and the subsequent time (HHMMSS)
        match = re.search(r"(\d{8})(\d{6})", data.path.name)
        if match:
            date_str = match.group(1)
            time_str = match.group(2)
            return (
                datetime.strptime(  # noqa: DTZ007
                    f"{date_str} {time_str}", "%Y%m%d %H%M%S"
                ),
                "Filename",
            )
        raise ValueError(f"Could not parse {data.path.name}")

    def f6() -> tuple[datetime, str]:
        """Get the datetime from the file modification date."""
        assert data.exif
        assert data.exif.file
        assert "FileModifyDate" in data.exif.file
        result = datetime.strptime(
            data.exif.file["FileModifyDate"],
            "%Y:%m:%d %H:%M:%S%z",
        )
        return result, "ModificationDate"

    for fn in [f1, f2, f3, f4, f5, f6]:
        try:
            return fn()
        except (KeyError, AssertionError, ValueError, AttributeError):  # noqa: PERF203
            continue
    raise ValueError(f"Could not parse datetime for {data.path.name}!")


def get_timezone_info(
    data: ImageData,
    date: datetime,
) -> tuple[datetime | None, str | None, timedelta | None]:
    """Gets timezone name and offset from latitude, longitude, and date."""
    if not data.time or not data.gps or not data.gps.latitude or not data.gps.longitude:
        return None, None, None

    timezone_name = timezone_finder.timezone_at(
        lat=data.gps.latitude,
        lng=data.gps.longitude,
    )
    if not timezone_name:
        return None, None, None

    tz_date = pytz.timezone(timezone_name).localize(date.replace(tzinfo=None))
    timezone_offset = tz_date.utcoffset()

    datetime_utc = data.time.datetime_utc
    if datetime_utc is None:
        datetime_utc = tz_date.astimezone(pytz.utc)

    return datetime_utc, timezone_name, timezone_offset


class TimeModule(PipelineModule[ImageData]):
    """Extracts datetime from an image."""

    depends: ClassVar[set[AnalyzerModule]] = {FileModule.EXIF, FileModule.GPS}

    def process(self, data: ImageData, _: FullAnalyzerConfig) -> None:
        """Extracts datetime from an image."""
        datetime_taken, datetime_source = get_local_datetime(data)
        datetime_utc, timezone_name, timezone_offset = get_timezone_info(data, datetime_taken)
        if datetime_utc is not None:
            datetime_utc = datetime_utc.replace(tzinfo=None)
        datetime_taken = datetime_taken.replace(tzinfo=None)

        data.time = TimeData(
            datetime_utc=datetime_utc,
            datetime_local=datetime_taken,
            datetime_source=datetime_source,
            timezone_name=timezone_name,
            timezone_offset=timezone_offset,
        )
