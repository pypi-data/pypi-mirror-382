from dataclasses import dataclass
from pathlib import Path

from media_analyzer.data.interfaces.frame_data import FrameDataOutput
from media_analyzer.data.interfaces.image_data import ImageDataOutput


@dataclass
class InputMedia:
    """Input for the media-analyzer package.

    Attributes:
        path: The path to the photo or video file.
        frames: A list of frame paths. In case of a photo, one frame is supplied,
            for a video you can generate multiple frames and submit them for analysis.
    """

    path: Path
    frames: list[Path]


@dataclass
class MediaAnalyzerOutput:
    """Output of the media-analyzer package.

    Attributes:
        image_data: File based analysis.
        frame_data: Visual analysis for the frames given in the input.
    """

    image_data: ImageDataOutput
    frame_data: list[FrameDataOutput]
