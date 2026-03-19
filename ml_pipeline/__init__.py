"""
ML Pipeline for Speed Radar - Vehicle Detection, Lane Detection, Tracking, and Speed Estimation.

This package contains modular components extracted from the Jupyter notebooks:
- 02_vehicle_detection_yolov9.ipynb
- 03_lane_detection_clrnet.ipynb
- 04_speed_estimation.ipynb
"""

from .vehicle_detector import VehicleDetector, CLASS_NAMES
from .lane_detector import LaneDetector, SimpleLaneDetector
from .tracker import SimpleTracker, VehicleTracker, calculate_iou
from .speed_calculator import (
    get_homography,
    calculate_meters_per_pixel,
    extract_line_segments,
)
from .pipeline import SpeedEstimationPipeline, extract_lane_polylines

__all__ = [
    # Vehicle Detection
    "VehicleDetector",
    "CLASS_NAMES",
    
    # Lane Detection
    "LaneDetector",
    "SimpleLaneDetector",
    
    # Tracking
    "SimpleTracker",
    "VehicleTracker",  # Backward compatibility
    "calculate_iou",
    
    # Speed Estimation
    "SpeedEstimationPipeline",
    "extract_lane_polylines",
    "get_homography",
    "calculate_meters_per_pixel",
    "extract_line_segments",
]

__version__ = "1.0.0"

