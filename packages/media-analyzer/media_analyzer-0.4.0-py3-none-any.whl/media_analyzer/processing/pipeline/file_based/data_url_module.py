import base64
from io import BytesIO

import PIL
import pillow_avif  # noqa: F401

from media_analyzer.data.anaylzer_config import FullAnalyzerConfig
from media_analyzer.data.interfaces.image_data import ImageData
from media_analyzer.processing.pipeline.pipeline_module import PipelineModule


class DataUrlModule(PipelineModule[ImageData]):
    """Convert an image to a data URL."""

    def process(self, data: ImageData, _: FullAnalyzerConfig) -> None:
        """Convert an image to a data URL."""
        tiny_height = 6
        with PIL.Image.open(data.frames[0]) as pil_image:
            img = pil_image.resize(
                (
                    int(pil_image.width / pil_image.height * tiny_height),
                    tiny_height,
                ),
            )
            buffered = BytesIO()
            img.save(buffered, format="PNG")
        data.data_url = base64.b64encode(buffered.getvalue()).decode()
