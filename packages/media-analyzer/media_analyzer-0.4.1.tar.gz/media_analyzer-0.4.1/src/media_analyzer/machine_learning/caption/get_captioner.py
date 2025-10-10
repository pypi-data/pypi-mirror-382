from media_analyzer.data.enums.config_types import CaptionerProvider, LLMProvider
from media_analyzer.machine_learning.caption.blip_captioner import BlipCaptioner
from media_analyzer.machine_learning.caption.captioner_protocol import CaptionerProtocol
from media_analyzer.machine_learning.caption.instruct_blip_captioner import InstructBlipCaptioner
from media_analyzer.machine_learning.caption.llm_captioner import LLMCaptioner


def get_captioner_by_provider(provider: CaptionerProvider) -> CaptionerProtocol:
    """Get the captioner by the provider.

    Args:
        provider: The captioner provider.

    Returns:
        The captioner.
    """
    return {
        CaptionerProvider.MINICPM: lambda: LLMCaptioner(LLMProvider.MINICPM),
        CaptionerProvider.OPENAI: lambda: LLMCaptioner(LLMProvider.OPENAI),
        CaptionerProvider.BLIP: BlipCaptioner,
        CaptionerProvider.BLIP_INSTRUCT: InstructBlipCaptioner,
    }[provider]()
