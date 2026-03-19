"""
Speed Estimation Pipeline - Complete End-to-End Pipeline

Integrates vehicle detection, lane detection, tracking, and speed estimation.

Extracted from notebook: 04_speed_estimation.ipynb
"""

import json
import logging
from collections import defaultdict, deque
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np
import torch
from PIL import Image
from torchvision import transforms

from .vehicle_detector import VehicleDetector
from .lane_detector import LaneDetector
from .tracker import SimpleTracker
from .speed_calculator import (
    get_homography,
    extract_line_segments,
    calculate_meters_per_pixel,
)

logger = logging.getLogger(__name__)


def extract_lane_polylines(
    mask: np.ndarray,
    threshold: float = 0.5,
    min_points: int = 10
) -> list:
    """
    Extract lane polylines from segmentation mask.

    Args:
        mask: Binary segmentation mask (H, W)
        threshold: Threshold for binarization
        min_points: Minimum number of points for a valid lane

    Returns:
        List of lane polylines, each as numpy array of (x, y) points
    """
    # Binarize mask
    binary_mask = (mask > threshold).astype(np.uint8) * 255

    # Find contours
    contours, _ = cv2.findContours(
        binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    lanes = []
    for contour in contours:
        # Approximate contour
        epsilon = 0.01 * cv2.arcLength(contour, False)  
        approx = cv2.approxPolyDP(contour, epsilon, False)

        # Convert to polyline
        points = approx.squeeze()

        if len(points.shape) == 2 and len(points) >= min_points:
            # Sort by y-coordinate
            points = points[np.argsort(points[:, 1])]
            lanes.append(points)

    return lanes


class SpeedEstimationPipeline:
    """
    Complete speed estimation pipeline integrating all components.

    Pipeline flow for each frame:
    1. Detect vehicles → bounding boxes
    2. Detect lanes → polylines
    3. Track vehicles → track IDs
    4. Calculate homography → bird's-eye view
    5. Measure lane spacing → meters-per-pixel
    6. Track vehicles in BEV → calculate speed
    """

    def __init__(
        self,
        vehicle_detector: VehicleDetector,
        lane_detector: Optional[LaneDetector],
        fps: float = 30.0,
        iou_threshold: float = 0.3,
        max_track_age: int = 30,
        output_dir: str = ".",
    ):
        """
        Initialize speed estimation pipeline.

        Args:
            vehicle_detector: VehicleDetector instance
            lane_detector: LaneDetector instance (can be None)
            fps: Video frames per second
            iou_threshold: IoU threshold for tracker
            max_track_age: Maximum frames to keep dead track
            output_dir: Directory to save vehicle crops and reports
        """
        self.vehicle_detector = vehicle_detector
        self.lane_detector = lane_detector
        self.fps = fps
        self.output_dir = Path(output_dir)

        # Create output directory if needed
        self.crops_dir = self.output_dir / "vehicle_crops"
        self.crops_dir.mkdir(parents=True, exist_ok=True)

        self.tracker = SimpleTracker(
            iou_threshold=iou_threshold,
            max_age=max_track_age
        )

        # Homography caching (computed once per video)
        self.homography_matrix = None
        self.meters_per_pixel = None
        self.frame_count = 0

        # Track history (BEV positions)
        self.track_history = defaultdict(lambda: deque(maxlen=20))
        self.track_speeds = defaultdict(lambda: deque(maxlen=20))
        
        # Track vehicle crops and bounding boxes
        self.track_crops = {}  # {track_id: crop_image_path}
        self.track_vehicles = {}  # {track_id: [x1, y1, x2, y2, class_id]}
        self.track_frame_count = defaultdict(int)  # {track_id: number_of_frames_seen}

    def process_frame(self, frame: np.ndarray) -> dict:
        """
        Process a single video frame through the pipeline.

        Args:
            frame: Input frame (BGR format from OpenCV)

        Returns:
            Dictionary with keys:
            - 'vehicles': List of [x1, y1, x2, y2, track_id, class_id, speed]
            - 'lanes': List of lane polylines
            - 'speeds': Dict of {track_id: speed_kmh}
        """
        h, w = frame.shape[:2]
        lanes = []

        # 1. Detect vehicles
        detections = self.vehicle_detector.detect(frame)
        logger.debug(f"Frame {self.frame_count}: {len(detections)} vehicles detected")

        # 2. Detect lanes & compute homography (only if not cached)
        if self.homography_matrix is None or self.meters_per_pixel is None:
            if self.lane_detector is not None:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                lane_mask = self.lane_detector.detect(frame_rgb)
                logger.debug(f"Frame {self.frame_count}: Lane mask returned: {lane_mask is not None}")

                if lane_mask is not None:
                    lanes = extract_lane_polylines(lane_mask, threshold=0.55, min_points=3)
                    logger.debug(f"Frame {self.frame_count}: Lane mask shape: {lane_mask.shape}, min: {lane_mask.min():.4f}, max: {lane_mask.max():.4f}")
                    logger.debug(f"Frame {self.frame_count}: Lanes extracted: {len(lanes)}")

                    if len(lanes) > 0:
                        try:
                            pil_image = Image.fromarray(frame_rgb)
                            warped, M = get_homography(pil_image, lane_mask)
                            logger.debug(f"Frame {self.frame_count}: Homography result - warped: {warped is not None}, M: {M is not None}")

                            if warped is not None and M is not None:
                                p_line, p_gap, _ = extract_line_segments(warped)
                                logger.debug(f"Frame {self.frame_count}: Line segments - p_line: {p_line}, p_gap: {p_gap}")
                                mpp = calculate_meters_per_pixel(p_line, p_gap)
                                logger.debug(f"Frame {self.frame_count}: MPP calculation result: {mpp}")

                                if mpp is not None:
                                    self.homography_matrix = M
                                    self.meters_per_pixel = mpp
                                    logger.info(f"--- SUCCESS: Scale Found at {mpp:.5f} MPP ---")
                        except Exception as e:
                            logger.warning(f"Homography calculation error: {e}")
                    else:
                        logger.debug(f"Frame {self.frame_count}: No lanes extracted")
                else:
                    logger.debug(f"Frame {self.frame_count}: Lane detector returned None mask")
            else:
                logger.warning("Lane detector is None")

        # 3. Track vehicles
        tracked_objects = self.tracker.update(detections)
        logger.debug(f"Frame {self.frame_count}: {len(tracked_objects)} vehicles tracked")

        # 4. Calculate speed and save crops ONLY for vehicles with valid speed
        speeds = {}
        vehicles_with_speed = []

        for obj in tracked_objects:
            x1, y1, x2, y2, track_id, class_id = obj
            track_id_int = int(track_id)
            cx, cy = (x1 + x2) / 2, y2  # Bottom-center for perspective

            current_speed = None

            # Only calculate if we have the road scale
            if self.homography_matrix is not None and self.meters_per_pixel is not None:
                point = np.array([[[cx, cy]]], dtype=np.float32)
                bev_point = cv2.perspectiveTransform(
                    point, self.homography_matrix
                )[0][0]
                self.track_history[track_id].append((self.frame_count, bev_point))

                # Calculate speed over 5-frame window for stability
                if len(self.track_history[track_id]) >= 5:
                    history = list(self.track_history[track_id])
                    (f_start, p_start), (f_end, p_end) = history[0], history[-1]

                    pixel_distance = np.linalg.norm(p_end - p_start)
                    dt = (f_end - f_start) / self.fps

                    if dt > 0:
                        meters = pixel_distance * self.meters_per_pixel
                        speed_kmh_raw = (meters / dt) * 3.6

                        # Filter outliers
                        if 5 < speed_kmh_raw < 220:
                            self.track_speeds[track_id].append(speed_kmh_raw)
                            current_speed = float(np.mean(self.track_speeds[track_id]))
                            speeds[track_id] = current_speed
                            logger.debug(f"Track {track_id_int}: Valid speed = {current_speed:.1f} km/h")

                            # Save crop ONLY once speed is verified (matches notebook)
                            if track_id_int not in self.track_crops:
                                try:
                                    pad = 10
                                    c_x1 = max(0, int(x1) - pad)
                                    c_y1 = max(0, int(y1) - pad)
                                    c_x2 = min(w, int(x2) + pad)
                                    c_y2 = min(h, int(y2) + pad)
                                    crop = frame[c_y1:c_y2, c_x1:c_x2]
                                    if crop.size > 0:
                                        crop_path = self.crops_dir / f"vehicle_{track_id_int}.jpg"
                                        cv2.imwrite(str(crop_path), crop)
                                        self.track_crops[track_id_int] = str(crop_path.name)
                                        self.track_vehicles[track_id_int] = [x1, y1, x2, y2, int(class_id)]
                                except Exception as e:
                                    logger.warning(f"Could not save crop for track {track_id_int}: {e}")
                        else:
                            logger.debug(f"Track {track_id_int}: Speed {speed_kmh_raw:.1f} km/h filtered out")

            # Track frame count for all tracked vehicles
            self.track_frame_count[track_id_int] += 1
            vehicles_with_speed.append((x1, y1, x2, y2, track_id, class_id, current_speed))

        self.frame_count += 1

        return {
            'vehicles': vehicles_with_speed,
            'lanes': lanes,
            'speeds': speeds,
        }

    def reset(self):
        """Reset pipeline state."""
        self.homography_matrix = None
        self.meters_per_pixel = None
        self.frame_count = 0
        self.tracker.reset()
        self.track_history.clear()
        self.track_speeds.clear()
        self.track_crops.clear()
        self.track_vehicles.clear()
        self.track_frame_count.clear()

    def generate_report(self) -> dict:
        """
        Generate final speed report with aggregated statistics.

        Returns:
            Dictionary with vehicle statistics ready to be saved as JSON
        """
        logger.info(f"Generating report: Total tracked vehicles with speeds: {len(self.track_speeds)}")
        report = {}
        
        for track_id, speeds in self.track_speeds.items():
            logger.debug(f"Track {int(track_id)}: {len(speeds)} speed measurements")
            if len(speeds) > 0:
                avg_speed = float(np.mean(speeds))
                max_speed = float(np.max(speeds))
                min_speed = float(np.min(speeds))
                
                crop_filename = self.track_crops.get(track_id, None)
                vehicle_info = self.track_vehicles.get(track_id, [0, 0, 0, 0, 0])
                class_id = int(vehicle_info[4]) if len(vehicle_info) > 4 else 0
                
                report[f"vehicle_{track_id}"] = {
                    "track_id": int(track_id),
                    "average_speed": round(avg_speed, 2),
                    "max_speed": round(max_speed, 2),
                    "min_speed": round(min_speed, 2),
                    "num_measurements": len(speeds),
                    "num_frames": self.track_frame_count.get(track_id, 0),
                    "image_filename": crop_filename,
                    "class_id": class_id,
                }
        
        return report

    def save_report(self, output_path: Optional[str] = None) -> str:
        """
        Generate and save the final speed report to JSON file.

        Args:
            output_path: Path to save the report. Defaults to output_dir/final_speed_report.json

        Returns:
            Path to the saved report file
        """
        if output_path is None:
            output_path = self.output_dir / "speed_report.json"
        else:
            output_path = Path(output_path)
        
        report = self.generate_report()
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved with {len(report)} vehicles to: {output_path}")
        
        logger.info(f"Report saved to: {output_path}")
        return str(output_path)

    def get_statistics(self) -> dict:
        """
        Get pipeline statistics.

        Returns:
            Dictionary with statistics
        """
        all_speeds = []
        for speeds in self.track_speeds.values():
            all_speeds.extend(speeds)

        if len(all_speeds) > 0:
            return {
                'total_measurements': len(all_speeds),
                'avg_speed': float(np.mean(all_speeds)),
                'max_speed': float(np.max(all_speeds)),
                'min_speed': float(np.min(all_speeds)),
                'std_speed': float(np.std(all_speeds)),
                'active_tracks': len(self.track_history),
            }
        else:
            return {
                'total_measurements': 0,
                'avg_speed': 0.0,
                'max_speed': 0.0,
                'min_speed': 0.0,
                'std_speed': 0.0,
                'active_tracks': len(self.track_history),
            }
