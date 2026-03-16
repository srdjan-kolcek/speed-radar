"""
Vehicle Detection Module - YOLOv9 Integration

Extracted from 04_speed_estimation.ipynb
"""

import logging
from pathlib import Path
from typing import List, Optional

import numpy as np
from ultralytics import YOLO

logger = logging.getLogger(__name__)


class VehicleDetector:
    """
    YOLOv9-based vehicle detector.

    Detects vehicles (cars, trucks, buses) in video frames.
    """

    def __init__(
        self,
        model_path: Optional[Path] = None,
        fallback_model: str = "yolov8m.pt",
        confidence_threshold: float = 0.25,
        iou_threshold: float = 0.45,
    ):
        """
        Initialize vehicle detector.

        Args:
            model_path: Path to trained YOLOv9 model weights
            fallback_model: Fallback model to use if model_path doesn't exist
            confidence_threshold: Minimum confidence for detections
            iou_threshold: IoU threshold for non-maximum suppression
        """
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold

        self.model = self._load_model(model_path, fallback_model)

    def _load_model(
        self,
        model_path: Optional[Path],
        fallback_model: str
    ) -> YOLO:
        """Load YOLO model."""
        try:
            if model_path and Path(model_path).exists():
                model = YOLO(str(model_path))
                logger.info(f"Loaded vehicle detector from: {model_path}")
            else:
                if model_path:
                    logger.warning(f"Model not found at {model_path}")
                logger.warning(f"Using fallback model: {fallback_model}")
                model = YOLO(fallback_model)

            model.model.eval()
            return model

        except Exception as e:
            logger.error(f"Error loading vehicle detector: {e}")
            raise

    def detect(self, frame: np.ndarray) -> List[List[float]]:
        """
        Detect vehicles in a frame.

        Args:
            frame: Input image (numpy array, RGB format)

        Returns:
            List of detections in format [x1, y1, x2, y2, confidence, class_id]
            where (x1, y1) is top-left corner and (x2, y2) is bottom-right corner
        """
        results = self.model.predict(
            frame,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            verbose=False
        )[0]

        detections = []
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            conf = float(box.conf[0].cpu().numpy())
            cls = int(box.cls[0].cpu().numpy())
            detections.append([x1, y1, x2, y2, conf, cls])

        return detections

    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model is not None
