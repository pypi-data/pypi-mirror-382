from media_analyzer.data.enums.config_types import EmbedderProvider
from media_analyzer.machine_learning.embedding.embedder_protocol import EmbedderProtocol
from media_analyzer.machine_learning.embedding.open_clip_embedder import OpenCLIPEmbedder
from media_analyzer.machine_learning.embedding.zero_clip_embedder import ZeroCLIPEmbedder

embedders: dict[EmbedderProvider, type[EmbedderProtocol]] = {
    EmbedderProvider.OPEN_CLIP: OpenCLIPEmbedder,
    EmbedderProvider.ZERO_CLIP: ZeroCLIPEmbedder,
}


def get_embedder_by_provider(provider: EmbedderProvider) -> EmbedderProtocol:
    """Get the LLM by the provider."""
    return embedders[provider]()
