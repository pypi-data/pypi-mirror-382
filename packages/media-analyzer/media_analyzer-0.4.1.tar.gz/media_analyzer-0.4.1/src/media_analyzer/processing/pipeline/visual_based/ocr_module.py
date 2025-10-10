from typing import TYPE_CHECKING

from media_analyzer.data.anaylzer_config import FullAnalyzerConfig
from media_analyzer.data.interfaces.frame_data import FrameData, OCRData
from media_analyzer.processing.pipeline.pipeline_module import PipelineModule

if TYPE_CHECKING:
    from media_analyzer.data.interfaces.ml_types import OCRBox


class OCRModule(PipelineModule[FrameData]):
    """Extract text from an image using OCR."""

    def process(self, data: FrameData, config: FullAnalyzerConfig) -> None:
        """Extract text from an image using OCR."""
        has_text = config.ocr.has_legible_text(data.image)
        extracted_text: str | None = None
        summary: str | None = None
        boxes: list[OCRBox] = []
        if has_text:
            extracted_text = config.ocr.get_text(data.image, config.settings.media_languages)
            if extracted_text.strip() == "":
                has_text = False
                extracted_text = None
            boxes = config.ocr.get_boxes(data.image, config.settings.media_languages)

        # Check if this could be a photo of a document
        if (
            config.settings.enable_document_summary
            and has_text
            and extracted_text
            and len(extracted_text) > config.settings.document_detection_threshold
        ):  # pragma: no cover
            prompt = (
                "Analyze the image and provide the following details:\n\n"
                "Summary: A concise summary of the content in the photo, including any"
                "key points or important sections visible."
                "Text Detection: Detect and list any legible text visible in the image."
                "If possible, extract it and provide a short excerpt or the full text."
                "Language Detection: Identify the language(s) in the text and specify the"
                "primary language used."
                "Document Type: Determine the type of document or text. Is it a formal"
                "document (e.g., letter, contract, form), informal (e.g., note, memo),"
                "or something else? Provide details about the document's likely purpose"
                "(e.g., invoice, receipt, report, etc.)."
                "Text Formatting: If relevant, describe any specific formatting styles"
                "such as headings, bullet points, numbered lists, tables, or signatures."
                "Additional Features: Detect if there are any images, logos, or other"
                "non-text elements present that provide additional context or information"
                "about the document (e.g., company logos, photos, charts)."
                "Contextual Details: If applicable, mention any visible date, address,"
                "or other contextual information that could help understand the document's"
                "origin or purpose."
            )

            summary = config.llm.image_question(data.image, prompt)

        data.ocr = OCRData(
            has_legible_text=has_text,
            ocr_text=extracted_text,
            document_summary=summary,
            ocr_boxes=boxes,
        )
