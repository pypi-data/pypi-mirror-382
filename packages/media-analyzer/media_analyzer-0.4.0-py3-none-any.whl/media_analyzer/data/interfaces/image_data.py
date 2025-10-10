from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from media_analyzer.data.enums.weather_condition import WeatherCondition
from media_analyzer.data.interfaces.location_types import GeoLocation


@dataclass
class ExifData:
    """Exif Data of the image.

    Attributes:
        width: The width of the image.
        height: The height of the image.
        duration: The duration of the media, if applicable.
        size_bytes: The size of the file in bytes.
        format: The format of the image.
        exif_tool: The output from ExifTool.
        file: File-related information.
        composite: Composite data.
        exif: Exif metadata, if available.
        xmp: XMP metadata, if available.
        mpf: Motion photo metadata, if available.
        jfif: JFIF metadata, if available.
        icc_profile: ICC profile data, if available.
        gif: GIF-specific data, if available.
        quicktime: QuickTime-specific data, if available.
        matroska: Matroska-specific data, if available.
    """

    width: int
    height: int
    duration: float | None
    size_bytes: int
    format: str
    exif_tool: dict[str, Any]
    file: dict[str, Any]
    composite: dict[str, Any]
    exif: dict[str, Any] | None
    xmp: dict[str, Any] | None
    mpf: dict[str, Any] | None
    jfif: dict[str, Any] | None
    icc_profile: dict[str, Any] | None
    gif: dict[str, Any] | None
    png: dict[str, Any] | None
    quicktime: dict[str, Any] | None
    matroska: dict[str, Any] | None


@dataclass
class GPSData:
    """GPS Data related to the image.

    Attributes:
        latitude: The latitude coordinate.
        longitude: The longitude coordinate.
        altitude: The altitude information.
        location: The geolocation information.
    """

    latitude: float | None = None
    longitude: float | None = None
    altitude: float | None = None
    location: GeoLocation | None = None


@dataclass
class IntermediateTimeData:
    """Intermediate Time Data related to the image, storing just datetime_utc."""

    datetime_utc: datetime | None = None


@dataclass
class TimeData:
    """Time-related data for the image.

    Attributes:
        datetime_local: The local datetime.
        datetime_source: The source of the datetime information.
        timezone_name: The name of the timezone.
        timezone_offset: The offset of the timezone.
        datetime_utc: The UTC datetime based of the GPS data.
    """

    datetime_local: datetime
    datetime_source: str
    timezone_name: str | None
    timezone_offset: timedelta | None
    datetime_utc: datetime | None = None


@dataclass
class WeatherData:
    """Weather data from the time and place the image was taken.

    Attributes:
        weather_recorded_at: The datetime when the weather was recorded.
        weather_temperature: The temperature at the time of recording.
        weather_dewpoint: The dew point at the time of recording.
        weather_relative_humidity: The relative humidity at the time of recording.
        weather_precipitation: The precipitation level at the time of recording.
        weather_wind_gust: The wind gust speed at the time of recording.
        weather_pressure: The atmospheric pressure at the time of recording.
        weather_sun_hours: The sun hours at the time of recording.
        weather_condition: The weather condition at the time of recording.
    """

    weather_recorded_at: datetime | None = None
    weather_temperature: float | None = None
    weather_dewpoint: float | None = None
    weather_relative_humidity: float | None = None
    weather_precipitation: float | None = None
    weather_wind_gust: float | None = None
    weather_pressure: float | None = None
    weather_sun_hours: float | None = None
    weather_condition: WeatherCondition | None = None


@dataclass
class TagData:
    """Tags, such as is_panorama, is_motion_photo, is_night_sight."""

    use_panorama_viewer: bool
    is_photosphere: bool
    projection_type: str | None
    is_motion_photo: bool
    motion_photo_presentation_timestamp: int | None
    is_night_sight: bool
    is_hdr: bool
    is_burst: bool
    burst_id: str | None
    is_timelapse: bool
    is_slowmotion: bool
    is_video: bool
    capture_fps: float | None
    video_fps: float | None


@dataclass
class ImageData:
    """Comprehensive data for an image.

    Attributes:
        path: The file system path to the image.
        frames: A list of frame paths associated with the image.
        exif: Exif data of the image.
        data_url: The data URL representation of the image.
        gps: GPS data associated with the image.
        time: Time-related data for the image.
        weather: Weather data at the time the image was taken.
    """

    path: Path
    frames: list[Path]
    exif: ExifData | None = None
    data_url: str | None = None
    gps: GPSData | None = None
    time: TimeData | IntermediateTimeData | None = None
    weather: WeatherData | None = None
    tags: TagData | None = None


@dataclass
class ImageDataOutput:
    """Comprehensive data for an image.

    Attributes:
        path: The file system path to the image.
        exif: Exif data of the image.
        data_url: The data URL representation of the image.
        gps: GPS data associated with the image.
        time: Time-related data for the image.
        weather: Weather data at the time the image was taken.
    """

    path: Path
    exif: ExifData | None = None
    data_url: str | None = None
    gps: GPSData | None = None
    time: TimeData | IntermediateTimeData | None = None
    weather: WeatherData | None = None
    tags: TagData | None = None
