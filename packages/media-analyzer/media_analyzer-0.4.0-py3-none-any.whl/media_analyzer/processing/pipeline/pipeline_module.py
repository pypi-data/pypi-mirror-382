from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar

from media_analyzer.data.interfaces.frame_data import FrameData
from media_analyzer.data.interfaces.image_data import ImageData

if TYPE_CHECKING:
    from media_analyzer.data.anaylzer_config import FullAnalyzerConfig
    from media_analyzer.data.enums.analyzer_module import AnalyzerModule

TData = TypeVar("TData", ImageData, FrameData)


class PipelineModule(ABC, Generic[TData]):
    """A generic pipeline module that can process either File-based or Visual data."""

    run_times: list[float]
    id: str
    depends: ClassVar[set[AnalyzerModule]] = set()

    def __init__(self) -> None:
        """Initializes the PipelineModule."""
        self.id = self.__class__.__name__
        self.run_times = []

    def run(self, data: TData, config: FullAnalyzerConfig) -> None:
        """Runs the pipeline module.

        Measuring the execution time and delegating the
        actual processing to the `process` method.

        Args:
            data: The data to be processed (ImageData or FrameData).
            config: The configuration object (e.g., FullAnalyzerConfig).
        """
        start_time = time.time()

        self.process(data, config)
        self.run_times.append(time.time() - start_time)

    @abstractmethod
    def process(self, data: TData, config: FullAnalyzerConfig) -> None:
        """Abstract method for processing data. This should be implemented by subclasses.

        Args:
            data: The data to be processed (ImageData or FrameData).
            config: The configuration object.
        """
