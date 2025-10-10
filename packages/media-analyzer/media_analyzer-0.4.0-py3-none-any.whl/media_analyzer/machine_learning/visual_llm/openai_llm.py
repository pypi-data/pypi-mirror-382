# pragma: exclude file
import base64
from collections.abc import Generator
from io import BytesIO
from typing import Any

from openai import OpenAI
from PIL.Image import Image

from media_analyzer.machine_learning.visual_llm.base_visual_llm import ChatMessage
from media_analyzer.machine_learning.visual_llm.mini_cpm_llm import MiniCPMLLM


def to_base64_url(image: Image, max_size: int = 720) -> str:
    """Convert an image to a base64 URL."""
    image.thumbnail((max_size, max_size))
    buffered = BytesIO()
    image.save(buffered, format="JPEG", optimize=True)
    b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


def chat_to_dict(chat: ChatMessage) -> dict[str, Any]:
    """Convert a ChatMessage to a dictionary."""
    if len(chat.images) == 0:
        return {
            "role": str(chat.role),
            "content": chat.message,
        }

    images = [
        {"type": "image_url", "image_url": {"url": to_base64_url(image)}} for image in chat.images
    ]
    return {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": chat.message,
            },
            *images,
        ],
    }


class OpenAILLM(MiniCPMLLM):
    """OpenAI LLM implementation."""

    model_name: str
    client: OpenAI

    def __init__(self, model_name: str = "gpt-4o-mini") -> None:
        """Initialize the OpenAI LLM."""
        super().__init__()
        self.model_name = model_name
        self.client = OpenAI()

    def stream_chat(
        self,
        messages: list[ChatMessage],
        convert_images: bool = True,  # noqa: ARG002
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> Generator[str, None, None]:  # pragma: no cover
        """OpenAI LLM chat that gives streaming output."""
        dict_messages = list(map(chat_to_dict, messages))

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=dict_messages,  # type: ignore[arg-type]
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )

        for chunk in response:
            chunk_content: str | None = chunk.choices[0].delta.content  # type: ignore[union-attr]
            if chunk_content is not None:
                yield chunk_content
