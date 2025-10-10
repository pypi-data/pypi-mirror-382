from media_analyzer.data.anaylzer_config import FullAnalyzerConfig
from media_analyzer.data.interfaces.frame_data import FrameData
from media_analyzer.processing.pipeline.pipeline_module import PipelineModule


class ObjectsModule(PipelineModule[FrameData]):
    """Detect objects in an image."""

    def process(self, data: FrameData, config: FullAnalyzerConfig) -> None:
        """Detect objects in an image."""
        data.objects = config.object_detector.detect_objects(data.image)
