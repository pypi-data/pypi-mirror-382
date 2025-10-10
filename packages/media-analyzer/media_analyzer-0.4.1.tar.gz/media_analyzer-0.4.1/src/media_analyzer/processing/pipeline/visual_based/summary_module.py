from media_analyzer.data.anaylzer_config import FullAnalyzerConfig
from media_analyzer.data.interfaces.frame_data import FrameData
from media_analyzer.processing.pipeline.pipeline_module import PipelineModule


class SummaryModule(PipelineModule[FrameData]):
    """Generate a summary from an image using a language model."""

    def process(self, data: FrameData, config: FullAnalyzerConfig) -> None:  # pragma: no cover
        """Generate a summary from an image using a language model."""
        if not config.settings.enable_text_summary:
            return
        prompt = (
            "Describe this image in a way that captures all essential details "
            "for a search database. Include the setting, key objects, actions, "
            "number and type of people or animals, and any noticeable visual "
            "features. Make the description clear, concise, and useful for "
            "someone searching this image in a library. Avoid subjective "
            "interpretations or ambiguous terms."
        )

        data.summary = config.llm.image_question(data.image, prompt)
