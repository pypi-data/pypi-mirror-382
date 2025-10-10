from enum import StrEnum, auto


class EmbedderProvider(StrEnum):
    """Embedder provider enums."""

    ZERO_CLIP = auto()
    OPEN_CLIP = auto()


class LLMProvider(StrEnum):
    """LLM providers enum."""

    MINICPM = auto()
    OPENAI = auto()


class CaptionerProvider(StrEnum):
    """Captioner providers enum."""

    BLIP_INSTRUCT = auto()
    MINICPM = auto()
    OPENAI = auto()
    BLIP = auto()
