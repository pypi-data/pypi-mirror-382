from enum import Enum


class WeatherCondition(Enum):
    """An enumeration of weather conditions."""

    CLEAR = 1
    FAIR = 2
    CLOUDY = 3
    OVERCAST = 4
    FOG = 5
    FREEZING_FOG = 6
    LIGHT_RAIN = 7
    RAIN = 8
    HEAVY_RAIN = 9
    FREEZING_RAIN = 10
    HEAVY_FREEZING_RAIN = 11
    SLEET = 12
    HEAVY_SLEET = 13
    LIGHT_SNOWFALL = 14
    SNOWFALL = 15
    HEAVY_SNOWFALL = 16
    RAIN_SHOWER = 17
    HEAVY_RAIN_SHOWER = 18
    SLEET_SHOWER = 19
    HEAVY_SLEET_SHOWER = 20
    SNOW_SHOWER = 21
    HEAVY_SNOW_SHOWER = 22
    LIGHTNING = 23
    HAIL = 24
    THUNDERSTORM = 25
    HEAVY_THUNDERSTORM = 26
    STORM = 27
