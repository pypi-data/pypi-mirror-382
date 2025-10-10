from media_analyzer.data.enums.config_types import LLMProvider
from media_analyzer.machine_learning.visual_llm.base_visual_llm import BaseVisualLLM
from media_analyzer.machine_learning.visual_llm.mini_cpm_llm import MiniCPMLLM
from media_analyzer.machine_learning.visual_llm.openai_llm import OpenAILLM

llm_providers: dict[LLMProvider, type[BaseVisualLLM]] = {
    LLMProvider.MINICPM: MiniCPMLLM,
    LLMProvider.OPENAI: OpenAILLM,
}


def get_llm_by_provider(provider: LLMProvider) -> BaseVisualLLM:
    """Get the LLM by the provider."""
    return llm_providers[provider]()
