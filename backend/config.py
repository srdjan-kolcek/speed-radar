"""
Configuration settings for Speed Radar API.
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models" / "weights"
UPLOADS_DIR = BASE_DIR / "backend" / "uploads"
OUTPUT_DIR = BASE_DIR / "backend" / "analysis_output"  # For vehicle crops and reports
# SAMPLE_VIDEOS_DIR = BASE_DIR / "sample_videos"

# Model paths
VEHICLE_MODEL_PATH = MODELS_DIR / "yolov9_vehicle_detection_best.pt"
LANE_MODEL_PATH = MODELS_DIR / "lane_detector_best.pt"

# Fallback models (if trained models don't exist)
FALLBACK_VEHICLE_MODEL = "yolov8m.pt"

# Video processing
MAX_VIDEO_SIZE_MB = 100
ALLOWED_VIDEO_FORMATS = [".mp4", ".avi", ".mov", ".MOV", ".MP4", ".AVI"]

# Speed calculation parameters
TRIPWIRE_Y1 = 200  # First tripwire y-position (bird's-eye view)
TRIPWIRE_Y2 = 600  # Second tripwire y-position (bird's-eye view)
DEFAULT_FPS = 30   # Default frames per second

# Detection parameters
MIN_CONFIDENCE = 0.8  # Minimum confidence for vehicle detection
IOU_THRESHOLD = 0.45   # IoU threshold for NMS
TRACKER_IOU_THRESHOLD = 0.2  # IoU threshold for tracking
TRACKER_MAX_AGE = 30   # Maximum frames to keep lost track

# Speed validation
MIN_VALID_SPEED_KMH = 20  # Minimum valid speed
MAX_VALID_SPEED_KMH = 150  # Maximum valid speed

# API settings
API_TITLE = "Speed Radar API"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
Speed Radar API for vehicle speed estimation from video footage.

Uses YOLOv9 for vehicle detection, CNN for lane detection, and homography-based
speed estimation with tripwire method.
"""

# CORS settings
ALLOWED_ORIGINS = ["*"]  # Allow all origins for development
