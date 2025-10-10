import cv2
import numpy as np
import numpy.typing as npt

from media_analyzer.data.anaylzer_config import FullAnalyzerConfig
from media_analyzer.data.interfaces.frame_data import FrameData, MeasuredQualityData
from media_analyzer.processing.pipeline.pipeline_module import PipelineModule


def sharpness_measurement(image: npt.NDArray[np.uint8]) -> float:
    """Measure image sharpness using Laplacian variance method.

    A higher variance indicates a sharper image.
    """
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
    return float(laplacian.var())


def exposure_measurement(image: npt.NDArray[np.uint8]) -> tuple[float, float]:
    """Measure image exposure by analyzing brightness and contrast.

    - Check mean brightness (underexposed if too dark, overexposed if too bright).
    - Check contrast (low contrast may indicate poor exposure).
    """
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray_image)  # type: ignore[arg-type]
    # Calculate contrast (standard deviation of pixel intensities)
    contrast = np.std(gray_image)  # type: ignore[arg-type]
    return float(mean_brightness), float(contrast)


def noise_measurement(image: npt.NDArray[np.uint8]) -> int:
    """Detect noise in an image by comparing the original image with a blurred version.

    - Higher differences between the original and blurred image indicate more noise.
    """
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    diff = cv2.absdiff(gray_image, blurred_image)
    return int(np.sum(diff))


def calculate_dynamic_range(image: npt.NDArray[np.uint8], sample_fraction: float = 0.1) -> float:
    """Calculate the dynamic range of an image by sampling the darkest and brightest pixels."""
    # Convert to grayscale if the image is in color
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # type: ignore[assignment]

    # Flatten the image into a 1D array and sort the pixel values
    flattened = image.flatten()
    sorted_pixels = np.sort(flattened)

    # Determine the number of pixels to sample
    num_pixels = len(sorted_pixels)
    sample_size = max(1, int(num_pixels * sample_fraction))  # Ensure at least 1 pixel is sampled

    # Get the mean of the darkest and brightest pixel samples
    darkest_mean = np.mean(sorted_pixels[:sample_size])
    brightest_mean = np.mean(sorted_pixels[-sample_size:])

    return float(brightest_mean - darkest_mean)


def measure_clipping(image: npt.NDArray[np.uint8]) -> float:
    """Calculate the percentage of clipped pixels (either 0 or 255) in a grayscale image."""
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # type: ignore[assignment]

    # Count the number of clipped pixels (0 or 255)
    total_pixels = image.size
    clipped_black = 0
    clipped_white = 255
    clipped_pixels = np.sum((image == clipped_black) | (image == clipped_white))

    # Calculate the percentage of clipped pixels
    return float(clipped_pixels / total_pixels)


def composite_quality_score(
    image: npt.NDArray[np.uint8],
    sharpness_weight: float = 2.0,
    exposure_weight: float = 1.0,
    noise_weight: float = 0.2,
    dynamic_range_weight: float = 1.0,
    clipping_weight: float = 1.0,
) -> float:
    """Combine image quality metrics into single score.

    Combine sharpness, exposure, noise, dynamic range and clipping
    into a single composite score from 0 to 1. Higher score indicates better image quality.
    Each score is weighted according to the specified weights.
    """
    sharpness_score = min(sharpness_measurement(image) / 2000.0, 1.0) * sharpness_weight

    mean_brightness, contrast = exposure_measurement(image)
    exposure_score = (
        ((1 - min(abs(mean_brightness - 160) / 160, 1)) + min(contrast / 100, 1.0))
        / 2
        * exposure_weight
    )

    noise_score = max(1 - min(noise_measurement(image) / 200000000.0, 1.0), 0.0) * noise_weight
    dynamic_range_score = min(calculate_dynamic_range(image) / 100, 1.0) * dynamic_range_weight
    clipping_score = max(1 - measure_clipping(image) / 0.1, 0.0) * clipping_weight

    # Combine scores and normalize
    total_weight = (
        sharpness_weight + exposure_weight + noise_weight + dynamic_range_weight + clipping_weight
    )
    return (
        sharpness_score + exposure_score + noise_score + dynamic_range_score + clipping_score
    ) / total_weight


class QualityDetectionModule(PipelineModule[FrameData]):
    """Detect image quality metrics."""

    def process(self, data: FrameData, _: FullAnalyzerConfig) -> None:
        """Detect image quality metrics."""
        image_cv2: npt.NDArray[np.uint8] = np.array(data.image)
        image_cv2 = cv2.cvtColor(image_cv2, cv2.COLOR_RGB2BGR)  # type: ignore[assignment]
        mean_brightness, contrast = exposure_measurement(image_cv2)
        data.measured_quality = MeasuredQualityData(
            measured_sharpness=sharpness_measurement(image_cv2),
            measured_noise=noise_measurement(image_cv2),
            measured_brightness=mean_brightness,
            measured_contrast=contrast,
            measured_clipping=measure_clipping(image_cv2),
            measured_dynamic_range=calculate_dynamic_range(image_cv2),
            quality_score=composite_quality_score(image_cv2),
        )
