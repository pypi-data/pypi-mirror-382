from collections.abc import Generator
from functools import lru_cache

import torch
from transformers import (
    AutoModel,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizerFast,
)

from media_analyzer.machine_learning.visual_llm.base_visual_llm import BaseVisualLLM, ChatMessage


@lru_cache
def get_model_and_tokenizer() -> tuple[PreTrainedModel, PreTrainedTokenizerFast]:
    """Retrieve and cache the model and tokenizer."""
    with torch.no_grad():
        model = AutoModel.from_pretrained(
            "openbmb/MiniCPM-V-2_6-int4",
            trust_remote_code=True,
        )
        model.eval()
        if torch.cuda.is_available():
            model.to(torch.device("cuda"))
        elif torch.backends.mps.is_available():  # pragma: no cover
            model.to(torch.device("mps"))
    tokenizer = AutoTokenizer.from_pretrained(  # type: ignore[no-untyped-call]
        "openbmb/MiniCPM-V-2_6-int4",
        trust_remote_code=True,
    )
    return model, tokenizer


class MiniCPMLLM(BaseVisualLLM):
    """Mini CPM LLM implementation."""

    def stream_chat(
        self,
        messages: list[ChatMessage],
        convert_images: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 500,  # noqa: ARG002
    ) -> Generator[str, None, None]:
        """Mini CPM LLM chat that gives streaming output."""
        if convert_images:
            for msg in messages:
                msg.images = [image.convert(mode="RGB") for image in msg.images]

        model, tokenizer = get_model_and_tokenizer()
        formatted_msgs = [
            {"role": msg.role.value.lower(), "content": [*msg.images, msg.message]}
            for msg in messages
        ]
        result = model.chat(  # type: ignore[operator]
            image=None,
            msgs=formatted_msgs,
            tokenizer=tokenizer,
            sampling=True,
            temperature=temperature,
            stream=True,
        )
        assert isinstance(result, Generator)
        return result
