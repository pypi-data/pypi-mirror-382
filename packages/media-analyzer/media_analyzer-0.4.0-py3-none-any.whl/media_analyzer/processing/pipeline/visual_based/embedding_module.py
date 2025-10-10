from media_analyzer.data.anaylzer_config import FullAnalyzerConfig
from media_analyzer.data.interfaces.frame_data import FrameData
from media_analyzer.processing.pipeline.pipeline_module import PipelineModule


class EmbeddingModule(PipelineModule[FrameData]):
    """Embed an image using CLIP."""

    def process(self, data: FrameData, config: FullAnalyzerConfig) -> None:
        """Embed an image using CLIP."""
        embedding = config.embedder.embed_image(data.image).tolist()
        assert isinstance(embedding, list)
        data.embedding = embedding
