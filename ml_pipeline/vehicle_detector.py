"""
Vehicle Detection Module - YOLOv9 Integration

Extracted from notebooks: 02_vehicle_detection_yolov9.ipynb and 04_speed_estimation.ipynb
"""

import logging
import os
from pathlib import Path
from typing import List, Optional

import numpy as np
from ultralytics import YOLO

logger = logging.getLogger(__name__)

# Class names for vehicle detection
CLASS_NAMES = ['car', 'truck', 'bus']


class VehicleDetector:
    """
    YOLOv9-based vehicle detector.
    Detects vehicles (cars, trucks, buses) in video frames.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
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

    def _load_model(self, model_path: Optional[str], fallback_model: str) -> YOLO:
        """Load YOLO model with fallback."""
        if model_path and os.path.exists(model_path):
            logger.info(f"Loading vehicle detector from: {model_path}")
            return YOLO(model_path)
        else:
            logger.warning(
                f"Model not found at {model_path}. "
                f"Using pretrained {fallback_model} instead."
            )
            return YOLO(fallback_model)

    def detect(self, frame: np.ndarray, verbose: bool = False) -> List[List[float]]:
        """
        Detect vehicles in a frame.

        Args:
            frame: Input frame (BGR format from OpenCV)
            verbose: Whether to log progress

        Returns:
            List of detections [x1, y1, x2, y2, confidence, class_id]
        """
        # Run detection
        results = self.model.predict(
            frame,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            verbose=False
        )[0]

        # Extract detections
        detections = []
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            conf = box.conf[0].cpu().numpy()
            cls = int(box.cls[0].cpu().numpy())
            detections.append([x1, y1, x2, y2, conf, cls])

        if verbose:
            logger.info(f"Detected {len(detections)} vehicles in frame")

        return detections

    def get_class_name(self, class_id: int) -> str:
        """Get class name from class ID."""
        if 0 <= class_id < len(CLASS_NAMES):
            return CLASS_NAMES[class_id]
        return "unknown"
