from abc import ABC, abstractmethod
from collections.abc import Generator
from dataclasses import dataclass, field
from enum import StrEnum, auto

from PIL.Image import Image


class ChatRole(StrEnum):
    """Chat roles enum."""

    ASSISTANT = auto()
    USER = auto()
    SYSTEM = auto()


@dataclass
class ChatMessage:
    """Chat message dataclass."""

    message: str
    images: list[Image] = field(default_factory=list)
    role: ChatRole = ChatRole.USER


class BaseVisualLLM(ABC):
    """Base class for visual language models."""

    def image_question(self, image: Image, question: str) -> str:
        """Ask a question about an image."""
        return self.images_question([image], question)

    def images_question(self, images: list[Image], question: str) -> str:
        """Ask a question about multiple images."""
        return str.join("", self.stream_chat([ChatMessage(message=question, images=images)]))

    @abstractmethod
    def stream_chat(
        self,
        messages: list[ChatMessage],
        convert_images: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> Generator[str, None, None]:
        """LLM chat that gives streaming output."""
