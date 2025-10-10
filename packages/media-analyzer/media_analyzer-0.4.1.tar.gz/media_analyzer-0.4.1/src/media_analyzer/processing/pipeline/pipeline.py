from typing import Any

import networkx as nx
import PIL.Image
import pillow_avif  # noqa: F401

from media_analyzer.data.anaylzer_config import FullAnalyzerConfig
from media_analyzer.data.enums.analyzer_module import AnalyzerModule, analyzer_module
from media_analyzer.data.interfaces.api_io import InputMedia
from media_analyzer.data.interfaces.frame_data import FrameData
from media_analyzer.data.interfaces.image_data import ImageData
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
from media_analyzer.processing.process_utils import pil_to_jpeg

pipeline_classes: list[type[PipelineModule[Any]]] = [
    DataUrlModule,
    ExifModule,
    GPSModule,
    TagsModule,
    TimeModule,
    WeatherModule,
    CaptionModule,
    EmbeddingModule,
    FacesModule,
    ObjectsModule,
    OCRModule,
    QualityDetectionModule,
    SummaryModule,
    ColorModule,
]
name_to_pipeline: dict[AnalyzerModule, type[PipelineModule[Any]]] = {
    analyzer_module(cls.__name__): cls for cls in pipeline_classes
}


def enum_to_pipeline(strings: list[AnalyzerModule]) -> list[type[PipelineModule[Any]]]:
    """Pipeline module id to pipeline module class."""
    return [name_to_pipeline[name] for name in strings]


def topological_sort(
    modules: set[type[PipelineModule[Any]]],
) -> list[PipelineModule[Any]]:
    """Sort modules topologically based on their dependencies."""
    graph = nx.DiGraph()
    for module in modules:
        graph.add_node(analyzer_module(module.__name__))
        for dependency in module.depends:
            graph.add_edge(analyzer_module(module.__name__), dependency)

    try:
        module_ids: list[AnalyzerModule] = list(reversed(list(nx.topological_sort(graph))))
        return [module() for module in enum_to_pipeline(module_ids)]
    except nx.NetworkXUnfeasible as e:
        raise ValueError(
            "A cycle was detected in the dependency graph, and topological sorting is not possible."
        ) from e


def run_metadata_pipeline(
    input_media: InputMedia,
    config: FullAnalyzerConfig,
) -> tuple[ImageData, list[FrameData]]:
    """Run the metadata pipeline on the input media."""
    image_data = ImageData(path=input_media.path, frames=input_media.frames)

    file_modules = topological_sort(
        {name_to_pipeline[name] for name in config.settings.enabled_file_modules}
    )
    for image_module in file_modules:
        image_module.run(image_data, config)

    frame_datas: list[FrameData] = []
    if len(config.settings.enabled_visual_modules) == 0:
        # Don't call pil_to_jpeg on frame path
        return image_data, frame_datas

    for frame_image_path in input_media.frames:
        with PIL.Image.open(frame_image_path) as frame_image:
            jpeg_image = pil_to_jpeg(frame_image)

        frame_data = FrameData(path=frame_image_path, image=jpeg_image)
        visual_modules = topological_sort(
            {name_to_pipeline[name] for name in config.settings.enabled_visual_modules}
        )

        for visual_module in visual_modules:
            visual_module.run(frame_data, config)
        frame_datas.append(frame_data)
        jpeg_image.close()

    return image_data, frame_datas
