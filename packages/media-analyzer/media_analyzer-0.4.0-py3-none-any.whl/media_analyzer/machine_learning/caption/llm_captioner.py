from PIL.Image import Image

from media_analyzer.data.enums.config_types import LLMProvider
from media_analyzer.machine_learning.caption.captioner_protocol import CaptionerProtocol
from media_analyzer.machine_learning.visual_llm.base_visual_llm import BaseVisualLLM
from media_analyzer.machine_learning.visual_llm.get_llm import get_llm_by_provider


class LLMCaptioner(CaptionerProtocol):
    """Captioner implementation using a large language model (LLM)."""

    llm_provider: BaseVisualLLM
    prompt: str = (
        "You are a BLIP image captioning model. "
        "Generate a short caption for this image. "
        "Examples: 'A plate of hotdogs', "
        "'A bedroom with a bed and chair', "
        "'A group of people by a lake', "
        "'A tabby cat on a bed'. "
        "Only output the caption!"
    )

    def __init__(self, provider: LLMProvider) -> None:
        """Initialize the LLM captioner."""
        self.llm_provider = get_llm_by_provider(provider)

    def caption(self, image: Image, instruction: str | None = None) -> str:
        """Generate a caption for the given image.

        Args:
            image: The image to caption.
            instruction: Optional instruction to prompt the caption model.
        """
        caption = self.llm_provider.image_question(
            image=image,
            question=self.prompt if instruction is None else instruction,
        )
        return caption.replace('"', "").replace("'", "")
