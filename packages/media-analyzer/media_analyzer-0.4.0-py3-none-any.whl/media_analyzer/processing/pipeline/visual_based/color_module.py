from typing import Any

import cv2
import numpy as np
import numpy.typing as npt
from material_color_utilities import (
    prominent_colors_from_image,
    theme_from_color,
)

from media_analyzer.data.anaylzer_config import FullAnalyzerConfig
from media_analyzer.data.interfaces.frame_data import ColorData, ColorHistogram, FrameData
from media_analyzer.processing.pipeline.pipeline_module import PipelineModule


def average_hue(hues: npt.NDArray[Any]) -> float:
    """Calculate the average hue (in degrees) from a list of hues."""
    # Convert hues to Cartesian coordinates
    radians = np.radians(hues)
    x = np.cos(radians)
    y = np.sin(radians)

    # Compute average x and y
    avg_x = np.mean(x)
    avg_y = np.mean(y)

    # Compute the average hue
    avg_hue = float(np.degrees(np.arctan2(avg_y, avg_x)))

    # Ensure the result is in the range [0, 360]
    if avg_hue < 0:
        avg_hue += 360

    return avg_hue


class ColorModule(PipelineModule[FrameData]):
    """Get Color info from an image."""

    def process(self, data: FrameData, config: FullAnalyzerConfig) -> None:
        """Get Color info from an image."""
        cv_image = np.array(data.image)
        image_hsv = cv2.cvtColor(cv_image, cv2.COLOR_RGB2HSV)

        # Extract the hue channel
        hue_channel = image_hsv[:, :, 0].flatten()
        saturation_channel = image_hsv[:, :, 1].flatten()
        lightness_channel = image_hsv[:, :, 2].flatten()

        # Convert hue values from OpenCV's [0, 179] range to [0, 360] range, and calculate avg hue.
        average_hue_value = average_hue(hue_channel * 2)
        average_saturation_value = float(saturation_channel.mean())
        average_lightness_value = float(lightness_channel.mean())

        prominent_colors = prominent_colors_from_image(data.image)[0:3]
        themes = [
            theme_from_color(
                color,
                variant=config.settings.theme_color_variant,
                contrast_level=config.settings.theme_contrast_level,
            )
            for color in prominent_colors
        ]

        # Calculate color histograms for each channel
        histogram_bins = 256
        red_hist = cv2.calcHist([cv_image], [0], None, [histogram_bins], [0, 256]).flatten()
        green_hist = cv2.calcHist([cv_image], [1], None, [histogram_bins], [0, 256]).flatten()
        blue_hist = cv2.calcHist([cv_image], [2], None, [histogram_bins], [0, 256]).flatten()

        # Convert histogram values from floats to ints
        red_ints = [int(x) for x in red_hist]
        green_ints = [int(x) for x in green_hist]
        blue_ints = [int(x) for x in blue_hist]

        histogram: ColorHistogram = {
            "bins": histogram_bins,
            "channels": {"red": red_ints, "green": green_ints, "blue": blue_ints},
        }

        data.color = ColorData(
            themes=[theme.dict() for theme in themes],
            prominent_colors=prominent_colors,
            average_hue=average_hue_value,
            average_saturation=average_saturation_value,
            average_lightness=average_lightness_value,
            histogram=histogram,
        )
