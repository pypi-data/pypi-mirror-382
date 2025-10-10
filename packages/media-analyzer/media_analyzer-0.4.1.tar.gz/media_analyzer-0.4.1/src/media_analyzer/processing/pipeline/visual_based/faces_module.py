from media_analyzer.data.anaylzer_config import FullAnalyzerConfig
from media_analyzer.data.interfaces.frame_data import FrameData
from media_analyzer.processing.pipeline.pipeline_module import PipelineModule


class FacesModule(PipelineModule[FrameData]):
    """Get faces from an image."""

    def process(self, data: FrameData, config: FullAnalyzerConfig) -> None:
        """Get faces from an image."""
        data.faces = config.facial_recognition.get_faces(data.image)
