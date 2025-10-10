"""
Python package for analyzing video/image with machine learning methods,
exif data, and other file based information."""

from media_analyzer.data.anaylzer_config import AnalyzerSettings, FullAnalyzerConfig
from media_analyzer.data.enums.analyzer_module import VisualModule, FileModule, AnalyzerModule
from media_analyzer.data.enums.config_types import CaptionerProvider, LLMProvider
from media_analyzer.data.enums.face_sex import FaceSex
from media_analyzer.data.interfaces.api_io import InputMedia, MediaAnalyzerOutput
from media_analyzer.data.interfaces.frame_data import MeasuredQualityData, FrameData, OCRData, \
    FrameDataOutput, ColorData, CaptionData, ColorHistogram
from media_analyzer.data.interfaces.image_data import ImageData, ExifData, GPSData, TimeData, \
    WeatherData, IntermediateTimeData, ImageDataOutput, TagData
from media_analyzer.data.interfaces.location_types import GeoLocation
from media_analyzer.data.interfaces.ml_types import FaceBox, ObjectBox, OCRBox, BaseBoundingBox
from media_analyzer.machine_learning.caption.blip_captioner import BlipCaptioner
from media_analyzer.machine_learning.caption.captioner_protocol import CaptionerProtocol
from media_analyzer.machine_learning.caption.get_captioner import get_captioner_by_provider
from media_analyzer.machine_learning.caption.llm_captioner import LLMCaptioner
from media_analyzer.machine_learning.embedding.embedder_protocol import EmbedderProtocol
from media_analyzer.machine_learning.embedding.open_clip_embedder import OpenCLIPEmbedder
from media_analyzer.machine_learning.embedding.zero_clip_embedder import ZeroCLIPEmbedder
from media_analyzer.machine_learning.facial_recognition.facial_recognition_protocol import (
    FacialRecognitionProtocol,
)
from media_analyzer.machine_learning.facial_recognition.insight_facial_recognition import (
    InsightFacialRecognition,
)
from media_analyzer.machine_learning.object_detection.object_detection_protocol import (
    ObjectDetectionProtocol,
)
from media_analyzer.machine_learning.object_detection.resnet_object_detection import (
    ResnetObjectDetection,
)
from media_analyzer.machine_learning.ocr.ocr_protocol import OCRProtocol
from media_analyzer.machine_learning.ocr.resnet_tesseract_ocr import ResnetTesseractOCR
from media_analyzer.machine_learning.visual_llm.base_visual_llm import BaseVisualLLM, ChatMessage, \
    ChatRole
from media_analyzer.machine_learning.visual_llm.get_llm import get_llm_by_provider
from media_analyzer.machine_learning.visual_llm.mini_cpm_llm import MiniCPMLLM
from media_analyzer.machine_learning.visual_llm.openai_llm import OpenAILLM
from media_analyzer.media_analyzer import MediaAnalyzer
from media_analyzer.processing.pipeline.file_based.data_url_module import DataUrlModule
from media_analyzer.processing.pipeline.file_based.exif_module import ExifModule
from media_analyzer.processing.pipeline.file_based.gps_module import GPSModule
from media_analyzer.processing.pipeline.file_based.tags_module import TagsModule
from media_analyzer.processing.pipeline.file_based.time_module import TimeModule
from media_analyzer.processing.pipeline.file_based.weather_module import WeatherModule
from media_analyzer.processing.pipeline.pipeline_module import PipelineModule
from media_analyzer.processing.pipeline.visual_based.caption_module import CaptionModule
from media_analyzer.processing.pipeline.visual_based.color_module import ColorModule
from media_analyzer.processing.pipeline.visual_based.embedding_module import EmbeddingModule
from media_analyzer.processing.pipeline.visual_based.faces_module import FacesModule
from media_analyzer.processing.pipeline.visual_based.objects_module import ObjectsModule
from media_analyzer.processing.pipeline.visual_based.ocr_module import OCRModule
from media_analyzer.processing.pipeline.visual_based.quality_detection_module import (
    QualityDetectionModule,
)
from media_analyzer.processing.pipeline.visual_based.summary_module import SummaryModule

__all__ = [
    # Main classes
    "MediaAnalyzer",
    "MediaAnalyzerOutput",
    "InputMedia",
    "AnalyzerSettings",
    "AnalyzerModule",
    "FileModule",
    "VisualModule",

    # Output data classes
    "ImageDataOutput",
    "FrameDataOutput",
    ## Image Data
    "ExifData",
    "GPSData",
    "TimeData",
    "WeatherData",
    "IntermediateTimeData",
    "TagData",
    ## Frame Data
    "OCRData",
    "CaptionData",
    "MeasuredQualityData",
    "ColorData",
    "ColorHistogram",

    # Extra output dataclasses
    "GeoLocation",
    "ChatMessage",
    "ChatRole",

    # Providers
    "get_llm_by_provider",
    "LLMProvider",
    "get_captioner_by_provider",
    "CaptionerProvider",

    # Modules
    "PipelineModule",
    ## File-based Modules
    "DataUrlModule",
    "ExifModule",
    "GPSModule",
    "TimeModule",
    "WeatherModule",
    "TagsModule",
    ## Visual-based Modules
    "CaptionModule",
    "EmbeddingModule",
    "SummaryModule",
    "FacesModule",
    "OCRModule",
    "ObjectsModule",
    "QualityDetectionModule",
    "ColorModule",

    # Machine learning classes
    "CaptionerProtocol",
    "BlipCaptioner",
    "EmbedderProtocol",
    "ZeroCLIPEmbedder",
    "OpenCLIPEmbedder",
    "FacialRecognitionProtocol",
    "InsightFacialRecognition",
    "ObjectDetectionProtocol",
    "ResnetObjectDetection",
    "OCRProtocol",
    "ResnetTesseractOCR",
    "LLMCaptioner",
    "BaseVisualLLM",
    "MiniCPMLLM",
    "OpenAILLM",

    # Machine learning types
    "BaseBoundingBox",
    "OCRBox",
    "ObjectBox",
    "FaceBox",
    "FaceSex",

    # Somewhat useless
    "FullAnalyzerConfig",
    "ImageData",
    "FrameData",
]
