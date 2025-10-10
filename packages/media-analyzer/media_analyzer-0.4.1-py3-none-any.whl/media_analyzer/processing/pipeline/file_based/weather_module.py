from datetime import timedelta
from typing import Any, ClassVar

from meteostat import Hourly, Point

from media_analyzer.data.anaylzer_config import FullAnalyzerConfig
from media_analyzer.data.enums.analyzer_module import AnalyzerModule, FileModule
from media_analyzer.data.enums.weather_condition import WeatherCondition
from media_analyzer.data.interfaces.image_data import ImageData, WeatherData
from media_analyzer.processing.pipeline.pipeline_module import PipelineModule


class WeatherModule(PipelineModule[ImageData]):
    """Extract weather data from the time and place an image was taken."""

    depends: ClassVar[set[AnalyzerModule]] = {FileModule.GPS}

    def process(self, data: ImageData, _: FullAnalyzerConfig) -> None:
        """Extract weather data from the time and place an image was taken."""
        if (
            not data.gps
            or not data.time
            or not data.time.datetime_utc
            or not data.gps.latitude
            or not data.gps.longitude
        ):
            return
        meteo_data = Hourly(
            Point(lat=data.gps.latitude, lon=data.gps.longitude),
            data.time.datetime_utc - timedelta(minutes=30),
            data.time.datetime_utc + timedelta(minutes=30),
        )
        meteo_data = meteo_data.fetch()
        if len(meteo_data) == 0:
            return  # pragma: no cover
        max_possible_rows = 2
        assert len(meteo_data) <= max_possible_rows
        weather = meteo_data.iloc[0]

        def panda_number(field: Any) -> int | None:  # noqa: ANN401
            try:
                return int(field)
            except (ValueError, TypeError):
                return None

        coco_number = panda_number(weather.coco)
        weather_condition = WeatherCondition(coco_number) if coco_number is not None else None
        data.weather = WeatherData(
            weather_recorded_at=weather.name.to_pydatetime(),
            weather_temperature=panda_number(weather.temp),
            weather_dewpoint=panda_number(weather.dwpt),
            weather_relative_humidity=panda_number(weather.rhum),
            weather_precipitation=panda_number(weather.prcp),
            weather_wind_gust=panda_number(weather.wpgt),
            weather_pressure=panda_number(weather.pres),
            weather_sun_hours=panda_number(weather.tsun),
            weather_condition=weather_condition,
        )
