from functools import lru_cache

import cv2
import numpy as np

from backend.app.core.config import get_settings
from backend.app.schemas.inspection import Classification, Detection, VisionResult


DEFECT_TERMS = ("defect", "crack", "scratch", "rust", "dent", "pit", "damage", "grease")


class BearingDetector:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.model = None
        self.load_error: str | None = None
        if self.settings.yolo_weights_path.exists():
            try:
                from ultralytics import YOLO

                self.model = YOLO(str(self.settings.yolo_weights_path))
            except Exception as exc:  # model/runtime errors must not crash capture
                self.load_error = str(exc)

    def inspect(self, image: np.ndarray, edges: np.ndarray) -> VisionResult:
        if self.model is not None:
            return self._run_yolo(image)
        return self._contour_fallback(image, edges)

    def _run_yolo(self, image: np.ndarray) -> VisionResult:
        prediction = self.model.predict(
            source=image,
            verbose=False,
        )[0]
        if prediction.probs is not None:
            return self._classification_result(prediction)

        names = prediction.names
        detections: list[Detection] = []
        for box in prediction.boxes:
            class_id = int(box.cls.item())
            x1, y1, x2, y2 = (int(value) for value in box.xyxy[0].tolist())
            detections.append(
                Detection(
                    label=str(names[class_id]),
                    confidence=round(float(box.conf.item()), 3),
                    box=(x1, y1, x2, y2),
                )
            )
        return VisionResult(
            mode="yolo",
            model_ready=True,
            model_version=self.settings.yolo_weights_path.name,
            detections=detections,
            note="Detections were produced by the configured local YOLO weights.",
        )

    def _classification_result(self, prediction) -> VisionResult:
        names = prediction.names
        probabilities = {
            str(names[index]): round(float(value), 4)
            for index, value in enumerate(prediction.probs.data.tolist())
        }
        class_id = int(prediction.probs.top1)
        label = str(names[class_id]).lower()
        confidence = round(float(prediction.probs.top1conf.item()), 4)
        return VisionResult(
            mode="yolo_classifier",
            model_ready=True,
            model_version=self.settings.yolo_weights_path.name,
            detections=[],
            classification=Classification(
                label=label,
                confidence=confidence,
                probabilities=probabilities,
            ),
            note="The local YOLO classifier assessed the complete bearing frame; no bounding box is implied.",
        )

    def _contour_fallback(self, image: np.ndarray, edges: np.ndarray) -> VisionResult:
        height, width = image.shape[:2]
        image_area = height * width
        expanded = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)
        contours, _ = cv2.findContours(expanded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detections: list[Detection] = []
        for contour in sorted(contours, key=cv2.contourArea, reverse=True):
            area_ratio = cv2.contourArea(contour) / image_area
            if not 0.0005 <= area_ratio <= 0.04:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            confidence = min(0.49, 0.18 + area_ratio * 8)
            detections.append(
                Detection(
                    label="unverified_anomaly_candidate",
                    confidence=round(confidence, 3),
                    box=(x, y, x + w, y + h),
                )
            )
            if len(detections) == 8:
                break
        detail = "YOLO weights are not installed; candidates come from OpenCV contours and cannot approve or reject a bearing."
        if self.load_error:
            detail += " The configured model could not be loaded."
        return VisionResult(
            mode="opencv_contour_fallback",
            model_ready=False,
            model_version="not_loaded",
            detections=detections,
            note=detail,
        )


def draw_overlay(image: np.ndarray, result: VisionResult) -> np.ndarray:
    overlay = image.copy()
    if result.classification is not None:
        label = result.classification.label.upper()
        confidence = result.classification.confidence
        color = (30, 220, 80) if label == "NORMAL" else (30, 80, 240)
        text = f"FRAME CLASSIFICATION: {label}  {confidence:.1%}"
        cv2.rectangle(overlay, (0, 0), (overlay.shape[1], 58), (18, 18, 18), -1)
        cv2.putText(overlay, text, (20, 39), cv2.FONT_HERSHEY_SIMPLEX, 0.85, color, 2, cv2.LINE_AA)
        return overlay
    color = (0, 185, 255) if not result.model_ready else (30, 220, 80)
    for detection in result.detections:
        x1, y1, x2, y2 = detection.box
        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)
        label = f"{detection.label} {detection.confidence:.2f}"
        cv2.putText(overlay, label, (x1, max(18, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)
    return overlay


@lru_cache
def get_detector() -> BearingDetector:
    return BearingDetector()
