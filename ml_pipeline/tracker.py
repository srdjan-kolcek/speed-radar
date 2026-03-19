"""
Vehicle Tracking Module - Simple IoU-Based Tracker

Extracted from notebook: 04_speed_estimation.ipynb
"""

import logging
from typing import List

logger = logging.getLogger(__name__)


def calculate_iou(box1: List[float], box2: List[float]) -> float:
    """
    Calculate Intersection over Union (IoU) between two bounding boxes.

    Args:
        box1: Bounding box [x1, y1, x2, y2]
        box2: Bounding box [x1, y1, x2, y2]

    Returns:
        IoU value (0.0 to 1.0)
    """
    x1_inter = max(box1[0], box2[0])
    y1_inter = max(box1[1], box2[1])
    x2_inter = min(box1[2], box2[2])
    y2_inter = min(box1[3], box2[3])

    if x2_inter < x1_inter or y2_inter < y1_inter:
        return 0.0

    inter_area = (x2_inter - x1_inter) * (y2_inter - y1_inter)
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = box1_area + box2_area - inter_area

    return inter_area / union_area if union_area > 0 else 0.0


class SimpleTracker:
    """
    Simple IoU-based tracker for vehicles.
    Tracks vehicles across frames using Intersection over Union (IoU) matching.
    This is a lightweight alternative to more complex trackers like ByteTrack.
    """

    def __init__(self, iou_threshold: float = 0.3, max_age: int = 30):
        """
        Initialize vehicle tracker.

        Args:
            iou_threshold: Minimum IoU for matching detections to tracks
            max_age: Maximum number of frames to keep a track without updates
        """
        self.iou_threshold = iou_threshold
        self.max_age = max_age
        self.tracks = {}
        self.next_id = 1
        self.frame_count = 0

    def update(self, detections: List[List[float]]) -> List[List[float]]:
        """
        Update tracks with new detections.

        Args:
            detections: List of detections [x1, y1, x2, y2, confidence, class_id]

        Returns:
            List of tracked objects [x1, y1, x2, y2, track_id, class_id]
        """
        self.frame_count += 1

        # Match detections to existing tracks
        matched_tracks = {}
        unmatched_detections = list(range(len(detections)))

        # Try to match each track
        for track_id, track_data in list(self.tracks.items()):
            best_iou = 0
            best_det_idx = -1

            for det_idx in unmatched_detections:
                det_box = detections[det_idx][:4]
                track_box = track_data["box"]
                iou = calculate_iou(track_box, det_box)

                if iou > best_iou and iou > self.iou_threshold:
                    best_iou = iou
                    best_det_idx = det_idx

            if best_det_idx >= 0:
                # Match found
                det = detections[best_det_idx]
                self.tracks[track_id] = {
                    "box": det[:4],
                    "class_id": int(det[5]) if len(det) > 5 else 0,
                    "last_seen": self.frame_count,
                }
                matched_tracks[track_id] = det[:4]
                unmatched_detections.remove(best_det_idx)

        # Create new tracks for unmatched detections
        for det_idx in unmatched_detections:
            det = detections[det_idx]
            track_id = self.next_id
            self.next_id += 1
            self.tracks[track_id] = {
                "box": det[:4],
                "class_id": int(det[5]) if len(det) > 5 else 0,
                "last_seen": self.frame_count,
            }
            matched_tracks[track_id] = det[:4]

        # Remove old tracks
        to_remove = []
        for track_id, track_data in self.tracks.items():
            if self.frame_count - track_data["last_seen"] > self.max_age:
                to_remove.append(track_id)

        for track_id in to_remove:
            del self.tracks[track_id]

        # Return tracked objects
        tracked_objects = []
        for track_id, box in matched_tracks.items():
            class_id = self.tracks[track_id]["class_id"]
            tracked_objects.append([*box, track_id, class_id])

        return tracked_objects

    def reset(self):
        """Reset tracker state."""
        self.tracks = {}
        self.next_id = 1
        self.frame_count = 0

    def get_active_tracks(self) -> dict:
        """
        Get currently active tracks.
        Returns:
            Dictionary of {track_id: track_data}
        """
        return self.tracks.copy()

    def get_track_count(self) -> int:
        """Get number of active tracks."""
        return len(self.tracks)


# For backward compatibility
VehicleTracker = SimpleTracker
