"""
Video Processing Module for Speed Estimation Pipeline

Processes videos through the complete ML pipeline and returns speed results.
"""

import logging
import tempfile
from pathlib import Path
from typing import Dict, List

import cv2
import numpy as np
from PIL import Image

# Import from the ml_pipeline package
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from ml_pipeline import (
    VehicleDetector,
    LaneDetector,
    VehicleTracker,
    SpeedCalculator,
    get_homography,
    extract_line_segments,
    calculate_meters_per_pixel,
)

from .config import (
    DEFAULT_FPS,
    LANE_MODEL_PATH,
    MIN_CONFIDENCE,
    IOU_THRESHOLD,
    TRACKER_IOU_THRESHOLD,
    TRACKER_MAX_AGE,
    TRIPWIRE_Y1,
    TRIPWIRE_Y2,
    MIN_VALID_SPEED_KMH,
    MAX_VALID_SPEED_KMH,
    VEHICLE_MODEL_PATH,
    FALLBACK_VEHICLE_MODEL,
)

logger = logging.getLogger(__name__)


class VideoProcessor:
    """
    Process videos through the complete speed estimation pipeline.

    Integrates vehicle detection, lane detection, tracking, and speed calculation.
    """

    def __init__(self):
        """Initialize video processor and load ML models."""
        logger.info("Initializing VideoProcessor...")

        # Initialize ML components
        self.vehicle_detector = VehicleDetector(
            model_path=VEHICLE_MODEL_PATH,
            fallback_model=FALLBACK_VEHICLE_MODEL,
            confidence_threshold=MIN_CONFIDENCE,
            iou_threshold=IOU_THRESHOLD,
        )

        self.lane_detector = LaneDetector(
            model_path=LANE_MODEL_PATH,
            input_size=(640, 640),
        )

        logger.info("VideoProcessor initialized successfully")

    def is_ready(self) -> bool:
        """
        Check if video processor is ready.

        Returns:
            True if models are loaded and ready
        """
        return (
            self.vehicle_detector is not None
            and self.vehicle_detector.is_loaded()
        )

    def process_video(self, video_path: str) -> Dict:
        """
        Process a video file and return speed estimations.

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with:
            {
                "results": List[dict],  # Speed measurements
                "total_frames": int,
                "fps": float,
                "successful": bool,
                "error": str (optional)
            }
        """
        try:
            # Open video
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                raise ValueError(f"Could not open video: {video_path}")

            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps == 0:
                logger.warning("Could not determine FPS, using default")
                fps = DEFAULT_FPS

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            logger.info(f"Processing video: {video_path}")
            logger.info(f"FPS: {fps}, Total frames: {total_frames}")

            # Initialize tracking and speed calculation
            tracker = VehicleTracker(
                iou_threshold=TRACKER_IOU_THRESHOLD,
                max_age=TRACKER_MAX_AGE,
            )

            speed_calculator = SpeedCalculator(
                tripwire_y1=TRIPWIRE_Y1,
                tripwire_y2=TRIPWIRE_Y2,
                fps=fps,
                min_valid_speed=MIN_VALID_SPEED_KMH,
                max_valid_speed=MAX_VALID_SPEED_KMH,
            )

            # State variables
            homography_matrix = None
            meters_per_pixel = None
            frame_count = 0

            # Aggregated results
            all_speeds = {}  # {track_id: [speeds]}
            vehicle_classes = {}  # {track_id: class_id}

            # Process frames
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1

                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Step 1: Detect vehicles
                detections = self.vehicle_detector.detect(frame_rgb)

                # Step 2: Track vehicles
                tracked_objects = tracker.update(detections)

                # Store vehicle classes
                for obj in tracked_objects:
                    track_id = int(obj[4])
                    class_id = int(obj[5])
                    vehicle_classes[track_id] = class_id

                # Step 3: Detect lanes (every 10 frames to save computation)
                if frame_count % 10 == 0 or homography_matrix is None:
                    lane_mask = self.lane_detector.detect(frame_rgb)

                    if lane_mask is not None:
                        # Calculate homography and scale
                        try:
                            pil_image = Image.fromarray(frame_rgb)
                            warped, M = get_homography(pil_image, lane_mask)

                            if warped is not None and M is not None:
                                homography_matrix = M

                                # Extract line segments
                                p_line, p_gap, _ = extract_line_segments(warped)

                                # Calculate scale
                                new_mpp = calculate_meters_per_pixel(p_line, p_gap)
                                if new_mpp is not None:
                                    meters_per_pixel = new_mpp

                        except Exception as e:
                            logger.debug(f"Homography calculation failed: {e}")

                # Step 4: Calculate speeds
                speeds = speed_calculator.update(
                    tracked_objects,
                    homography_matrix,
                    meters_per_pixel,
                )

                # Aggregate speeds per track
                for track_id, speed in speeds.items():
                    if track_id not in all_speeds:
                        all_speeds[track_id] = []

                    all_speeds[track_id].append(speed)

                # Log progress
                if frame_count % 100 == 0:
                    logger.info(f"Processed {frame_count}/{total_frames} frames...")

            cap.release()

            # Calculate final results
            results = self._aggregate_results(all_speeds, vehicle_classes)

            logger.info(f"Processing complete. Total frames: {frame_count}")
            logger.info(f"Vehicles tracked: {len(results)}")

            return {
                "results": results,
                "total_frames": frame_count,
                "fps": fps,
                "successful": True,
            }

        except Exception as e:
            logger.error(f"Error processing video: {e}", exc_info=True)
            return {
                "results": [],
                "total_frames": 0,
                "fps": 0,
                "successful": False,
                "error": str(e),
            }

    def _aggregate_results(
        self,
        all_speeds: Dict[int, List[float]],
        vehicle_classes: Dict[int, int],
    ) -> List[Dict]:
        """
        Aggregate multiple speed measurements per vehicle.

        Args:
            all_speeds: Dictionary of {track_id: [speeds]}
            vehicle_classes: Dictionary of {track_id: class_id}

        Returns:
            List of speed result dictionaries
        """
        results = []
        class_names = {0: "car", 1: "truck", 2: "bus"}

        for track_id, speeds in all_speeds.items():
            if len(speeds) == 0:
                continue

            # Calculate average speed
            avg_speed = np.mean(speeds)

            # Calculate confidence based on consistency
            if len(speeds) > 1:
                std_speed = np.std(speeds)
                # Lower std = higher confidence
                confidence = max(0.5, min(1.0, 1.0 - (std_speed / avg_speed)))
            else:
                confidence = 0.7  # Single measurement

            # Get vehicle type
            class_id = vehicle_classes.get(track_id, 0)
            vehicle_type = class_names.get(class_id, "vehicle")

            results.append({
                "track_id": int(track_id),
                "speed_kmh": float(avg_speed),
                "confidence": float(confidence),
                "vehicle_type": vehicle_type,
            })

        # Sort by track_id
        results.sort(key=lambda x: x["track_id"])

        return results

    def save_upload(self, upload_file, max_size_mb: int = 100) -> Path:
        """
        Save uploaded video to temporary location.

        Args:
            upload_file: FastAPI UploadFile object
            max_size_mb: Maximum file size in MB

        Returns:
            Path to saved file

        Raises:
            ValueError: If file is too large or invalid format
        """
        # Check file size
        upload_file.file.seek(0, 2)  # Seek to end
        file_size = upload_file.file.tell()
        upload_file.file.seek(0)  # Seek back to start

        size_mb = file_size / (1024 * 1024)
        if size_mb > max_size_mb:
            raise ValueError(
                f"File too large: {size_mb:.2f}MB (max: {max_size_mb}MB)"
            )

        # Create temporary file
        suffix = Path(upload_file.filename).suffix
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)

        try:
            # Write uploaded file to temp file
            temp_file.write(upload_file.file.read())
            temp_file.close()

            logger.info(f"Saved upload to: {temp_file.name}")
            return Path(temp_file.name)

        except Exception as e:
            temp_file.close()
            Path(temp_file.name).unlink(missing_ok=True)
            raise ValueError(f"Error saving upload: {e}")

    def get_video_info(self, video_path: str) -> Dict:
        """
        Get information about a video file.

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with video properties
        """
        try:
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                return {"error": "Could not open video"}

            info = {
                "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "fps": float(cap.get(cv2.CAP_PROP_FPS)),
                "total_frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                "duration_seconds": 0,
            }

            if info["fps"] > 0:
                info["duration_seconds"] = info["total_frames"] / info["fps"]

            cap.release()
            return info

        except Exception as e:
            return {"error": str(e)}
