from dataclasses import dataclass


@dataclass
class GeoLocation:
    """Represents a reverse geocoded location where a photo/video was taken.

    Attributes:
        country: The country name.
        city: The city name.
        province: The province or state name, if applicable.
        place_latitude: The latitude coordinate of the location.
        place_longitude: The longitude coordinate of the location.
    """

    country: str
    city: str
    province: str | None
    place_latitude: float
    place_longitude: float
