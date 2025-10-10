from pathlib import Path

from media_analyzer.data.anaylzer_config import AnalyzerSettings, FullAnalyzerConfig
from media_analyzer.data.interfaces.api_io import InputMedia, MediaAnalyzerOutput
from media_analyzer.data.interfaces.frame_data import FrameDataOutput
from media_analyzer.data.interfaces.image_data import ImageDataOutput
from media_analyzer.machine_learning.caption.get_captioner import get_captioner_by_provider
from media_analyzer.machine_learning.embedding.get_embedder import get_embedder_by_provider
from media_analyzer.machine_learning.facial_recognition.insight_facial_recognition import (
    InsightFacialRecognition,
)
from media_analyzer.machine_learning.object_detection.resnet_object_detection import (
    ResnetObjectDetection,
)
from media_analyzer.machine_learning.ocr.resnet_tesseract_ocr import ResnetTesseractOCR
from media_analyzer.machine_learning.visual_llm.get_llm import get_llm_by_provider
from media_analyzer.processing.pipeline.pipeline import run_metadata_pipeline


class MediaAnalyzer:
    """Analyze media using a machine learning models, file based analysis, and exif data."""

    config: FullAnalyzerConfig

    def __init__(self, config: AnalyzerSettings | None = None) -> None:
        """Initialize the media analyzer with the given configuration."""
        if config is None:
            config = AnalyzerSettings()
        embedder = get_embedder_by_provider(config.embedder_provider)
        self.config = FullAnalyzerConfig(
            llm=get_llm_by_provider(config.llm_provider),
            captioner=get_captioner_by_provider(config.captions_provider),
            ocr=ResnetTesseractOCR(),
            object_detector=ResnetObjectDetection(),
            facial_recognition=InsightFacialRecognition(),
            embedder=embedder,
            settings=config,
        )

    def analyze(self, input_media: InputMedia) -> MediaAnalyzerOutput:
        """Analyze the given photo or video."""
        image_data, frame_data = run_metadata_pipeline(input_media, self.config)
        image_data_output = ImageDataOutput(
            path=image_data.path,
            exif=image_data.exif,
            data_url=image_data.data_url,
            gps=image_data.gps,
            time=image_data.time,
            weather=image_data.weather,
            tags=image_data.tags,
        )
        frame_output = [
            FrameDataOutput(
                ocr=frame.ocr,
                embedding=frame.embedding,
                faces=frame.faces,
                summary=frame.summary,
                caption_data=frame.caption_data,
                objects=frame.objects,
                measured_quality=frame.measured_quality,
                color=frame.color,
            )
            for frame in frame_data
        ]
        return MediaAnalyzerOutput(image_data=image_data_output, frame_data=frame_output)

    def photo(self, image_path: Path) -> MediaAnalyzerOutput:
        """Analyze a photo."""
        return self.analyze(InputMedia(image_path, frames=[image_path]))
