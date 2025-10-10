from functools import lru_cache

import cv2
import numpy as np
from insightface.app import FaceAnalysis
from PIL.Image import Image

from media_analyzer.data.enums.face_sex import FaceSex
from media_analyzer.data.interfaces.ml_types import FaceBox
from media_analyzer.machine_learning.facial_recognition.facial_recognition_protocol import (
    FacialRecognitionProtocol,
)
from media_analyzer.machine_learning.utils import coordinate_to_proportional


@lru_cache
def get_app() -> FaceAnalysis:
    """Get the InsightFace app."""
    app = FaceAnalysis(
        root="~/.cache/insightface",
        providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
    )
    app.prepare(ctx_id=0, det_size=(640, 640))
    return app


class InsightFacialRecognition(FacialRecognitionProtocol):
    """Facial recognition implementation using the InsightFace model."""

    def get_faces(self, image: Image) -> list[FaceBox]:
        """Detect and embed faces from an image."""
        cv_image = np.array(image)
        dims_in_image = 3
        if cv_image.shape[2] == dims_in_image:
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
        app = get_app()
        faces = app.get(cv_image)
        return [
            FaceBox(
                position=coordinate_to_proportional(face.bbox.tolist(), image),
                width=(face.bbox[2] - face.bbox[0]).item() / image.width,
                height=(face.bbox[3] - face.bbox[1]).item() / image.height,
                age=face.age,
                sex=FaceSex(face.sex),
                confidence=face.det_score.item(),
                mouth_left=coordinate_to_proportional(face.kps[0].tolist(), image),
                mouth_right=coordinate_to_proportional(face.kps[1].tolist(), image),
                nose_tip=coordinate_to_proportional(face.kps[2].tolist(), image),
                eye_left=coordinate_to_proportional(face.kps[3].tolist(), image),
                eye_right=coordinate_to_proportional(face.kps[4].tolist(), image),
                embedding=face.normed_embedding.tolist(),
            )
            for face in faces
        ]
