"""
ML Pipeline for Speed Radar - Vehicle Detection, Lane Detection, Tracking, and Speed Estimation.

This package contains modular components extracted from the Jupyter notebooks.
"""

from .vehicle_detector import VehicleDetector
from .lane_detector import LaneDetector, SimpleLaneDetector
from .tracker import VehicleTracker
from .speed_calculator import (
    SpeedCalculator,
    get_homography,
    calculate_meters_per_pixel,
    extract_line_segments,
)

__all__ = [
    "VehicleDetector",
    "LaneDetector",
    "SimpleLaneDetector",
    "VehicleTracker",
    "SpeedCalculator",
    "get_homography",
    "calculate_meters_per_pixel",
    "extract_line_segments",
]

__version__ = "1.0.0"
