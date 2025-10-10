import re
from typing import ClassVar

from media_analyzer.data.anaylzer_config import FullAnalyzerConfig
from media_analyzer.data.enums.analyzer_module import AnalyzerModule, FileModule
from media_analyzer.data.interfaces.image_data import ImageData, TagData
from media_analyzer.processing.pipeline.pipeline_module import PipelineModule


def detect_burst(filename: str) -> tuple[bool, str | None]:
    """Detect if a filename indicates it's a burst photo."""
    if "burst" not in filename.lower():
        return False, None

    # Match the Google Pixel format: BURST followed by 17 digits
    burst_pattern1 = re.compile(r"BURST(\d{17})", re.IGNORECASE)
    match1 = burst_pattern1.search(filename)
    if match1:
        is_burst = True
        burst_id = match1.group(1)
        return is_burst, burst_id

    # Match the alternate format: <date>_<time>_Burst<number>
    burst_pattern2 = re.compile(r"(.*?)_Burst\d+", re.IGNORECASE)
    match2 = burst_pattern2.search(filename)
    if match2:
        is_burst = True
        burst_id = match2.group(1)
        return is_burst, burst_id

    return False, None


class TagsModule(PipelineModule[ImageData]):
    """Extract weather data from the time and place an image was taken."""

    depends: ClassVar[set[AnalyzerModule]] = {FileModule.EXIF}

    def process(self, data: ImageData, _: FullAnalyzerConfig) -> None:
        """Get tags such as is_panorama, is_night_sight, is_motion_photo, etc."""
        assert data.exif is not None

        is_hdr = "hdr" in data.path.name.lower()
        is_burst, burst_id = detect_burst(data.path.name)
        is_timelapse = False
        is_slowmotion = False
        is_photosphere = False
        is_night_sight = "night" in data.path.name.lower()
        is_video = "video" in data.exif.file["MIMEType"]
        is_motion_photo = False
        projection_type: str | None = None
        capture_fps: float | None = None
        video_fps: float | None = None
        use_panorama_viewer = False
        motion_photo_presentation_timestamp: int | None = None

        # Photosphere / Motion Photo
        if data.exif.xmp:
            use_panorama_viewer = data.exif.xmp.get("UsePanoramaViewer", False)
            is_photosphere = data.exif.xmp.get("IsPhotosphere", False)
            projection_type = data.exif.xmp.get("ProjectionType", None)
            is_motion_photo = data.exif.xmp.get("MotionPhoto", 0) == 1
            if is_motion_photo:
                motion_photo_presentation_timestamp = data.exif.xmp.get(
                    "MotionPhotoPresentationTimestampUs"
                )

            if "BurstID" in data.exif.xmp:
                is_burst = True
                burst_id = data.exif.xmp["BurstID"]

        # Slowmotion
        if data.exif.quicktime:
            capture_fps = data.exif.quicktime.get("AndroidCaptureFPS")
            video_fps = data.exif.quicktime.get("VideoFrameRate")
            if capture_fps and video_fps and capture_fps > video_fps + 1:
                is_slowmotion = True

            special_type = data.exif.quicktime.get("SpecialTypeID")
            if special_type:
                is_timelapse = "timelapse" in special_type.lower()

        data.tags = TagData(
            is_video=is_video,
            capture_fps=capture_fps,
            video_fps=video_fps,
            is_hdr=is_hdr,
            is_burst=is_burst,
            burst_id=burst_id,
            is_timelapse=is_timelapse,
            is_slowmotion=is_slowmotion,
            is_photosphere=is_photosphere,
            is_night_sight=is_night_sight,
            is_motion_photo=is_motion_photo,
            projection_type=projection_type,
            use_panorama_viewer=use_panorama_viewer,
            motion_photo_presentation_timestamp=motion_photo_presentation_timestamp,
        )
