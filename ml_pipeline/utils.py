"""
Utility Functions for ML Pipeline

Helper functions for visualization and common operations.
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional


def draw_bounding_box(
    image: np.ndarray,
    box: List[float],
    color: Tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2,
    label: Optional[str] = None
) -> np.ndarray:
    """
    Draw a bounding box on an image.

    Args:
        image: Input image (numpy array)
        box: Bounding box [x1, y1, x2, y2]
        color: Box color (B, G, R)
        thickness: Line thickness
        label: Optional text label

    Returns:
        Image with bounding box drawn
    """
    x1, y1, x2, y2 = map(int, box[:4])

    # Draw rectangle
    cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)

    # Draw label if provided
    if label:
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        font_thickness = 1

        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(
            label, font, font_scale, font_thickness
        )

        # Draw background rectangle for text
        cv2.rectangle(
            image,
            (x1, y1 - text_height - baseline - 5),
            (x1 + text_width, y1),
            color,
            -1
        )

        # Draw text
        cv2.putText(
            image,
            label,
            (x1, y1 - baseline - 5),
            font,
            font_scale,
            (255, 255, 255),
            font_thickness
        )

    return image


def draw_detections(
    image: np.ndarray,
    detections: List[List[float]],
    class_names: dict = None
) -> np.ndarray:
    """
    Draw all detections on an image.

    Args:
        image: Input image (numpy array)
        detections: List of detections [x1, y1, x2, y2, conf, class_id]
        class_names: Dictionary mapping class_id to class name

    Returns:
        Image with detections drawn
    """
    if class_names is None:
        class_names = {0: "car", 1: "truck", 2: "bus"}

    colors = {
        0: (0, 255, 0),    # Green for cars
        1: (255, 0, 0),    # Blue for trucks
        2: (0, 0, 255),    # Red for buses
    }

    result = image.copy()

    for det in detections:
        x1, y1, x2, y2, conf, cls = det
        class_id = int(cls)
        class_name = class_names.get(class_id, "vehicle")
        color = colors.get(class_id, (255, 255, 255))

        label = f"{class_name} {conf:.2f}"
        result = draw_bounding_box(result, [x1, y1, x2, y2], color, 2, label)

    return result


def draw_tracked_objects(
    image: np.ndarray,
    tracked_objects: List[List[float]],
    speeds: dict = None,
    class_names: dict = None
) -> np.ndarray:
    """
    Draw tracked objects with IDs and speeds on an image.

    Args:
        image: Input image (numpy array)
        tracked_objects: List of [x1, y1, x2, y2, track_id, class_id]
        speeds: Optional dictionary {track_id: speed_kmh}
        class_names: Dictionary mapping class_id to class name

    Returns:
        Image with tracked objects drawn
    """
    if class_names is None:
        class_names = {0: "car", 1: "truck", 2: "bus"}

    colors = {
        0: (0, 255, 0),    # Green for cars
        1: (255, 0, 0),    # Blue for trucks
        2: (0, 0, 255),    # Red for buses
    }

    result = image.copy()

    for obj in tracked_objects:
        x1, y1, x2, y2, track_id, class_id = obj
        class_id = int(class_id)
        track_id = int(track_id)
        class_name = class_names.get(class_id, "vehicle")
        color = colors.get(class_id, (255, 255, 255))

        label = f"ID:{track_id} {class_name}"

        # Add speed if available
        if speeds and track_id in speeds:
            speed = speeds[track_id]
            label += f" {speed:.1f}km/h"

        result = draw_bounding_box(result, [x1, y1, x2, y2], color, 2, label)

    return result


def draw_lane_mask(
    image: np.ndarray,
    mask: np.ndarray,
    color: Tuple[int, int, int] = (255, 255, 0),
    alpha: float = 0.5
) -> np.ndarray:
    """
    Overlay lane segmentation mask on image.

    Args:
        image: Input image (numpy array, RGB)
        mask: Lane mask (H, W) with values 0-1
        color: Overlay color (R, G, B)
        alpha: Transparency (0-1)

    Returns:
        Image with mask overlay
    """
    result = image.copy()

    # Resize mask to match image size if needed
    if mask.shape[:2] != image.shape[:2]:
        mask = cv2.resize(mask, (image.shape[1], image.shape[0]))

    # Create colored overlay
    overlay = np.zeros_like(image)
    overlay[mask > 0.5] = color

    # Blend with original image
    result = cv2.addWeighted(result, 1 - alpha, overlay, alpha, 0)

    return result


def draw_tripwires(
    image: np.ndarray,
    tripwire_y1: int,
    tripwire_y2: int,
    homography_matrix: Optional[np.ndarray] = None,
    color: Tuple[int, int, int] = (0, 255, 255),
    thickness: int = 2
) -> np.ndarray:
    """
    Draw tripwire lines on image.

    Args:
        image: Input image (numpy array)
        tripwire_y1: First tripwire y-coordinate (bird's-eye view)
        tripwire_y2: Second tripwire y-coordinate (bird's-eye view)
        homography_matrix: Optional homography matrix to transform back to original view
        color: Line color (B, G, R)
        thickness: Line thickness

    Returns:
        Image with tripwires drawn
    """
    result = image.copy()
    h, w = image.shape[:2]

    if homography_matrix is not None:
        # Transform tripwires back to original image coordinates
        try:
            inv_H = np.linalg.inv(homography_matrix)

            # Create line points in bird's-eye view
            points_y1 = np.array([[[0, tripwire_y1], [400, tripwire_y1]]], dtype=np.float32)
            points_y2 = np.array([[[0, tripwire_y2], [400, tripwire_y2]]], dtype=np.float32)

            # Transform to original view
            transformed_y1 = cv2.perspectiveTransform(points_y1, inv_H)
            transformed_y2 = cv2.perspectiveTransform(points_y2, inv_H)

            # Draw lines
            pt1_y1 = tuple(map(int, transformed_y1[0][0]))
            pt2_y1 = tuple(map(int, transformed_y1[0][1]))
            pt1_y2 = tuple(map(int, transformed_y2[0][0]))
            pt2_y2 = tuple(map(int, transformed_y2[0][1]))

            cv2.line(result, pt1_y1, pt2_y1, color, thickness)
            cv2.line(result, pt1_y2, pt2_y2, color, thickness)

        except Exception:
            # If transformation fails, draw horizontal lines
            cv2.line(result, (0, tripwire_y1), (w, tripwire_y1), color, thickness)
            cv2.line(result, (0, tripwire_y2), (w, tripwire_y2), color, thickness)
    else:
        # Draw horizontal lines at specified y-coordinates
        cv2.line(result, (0, tripwire_y1), (w, tripwire_y1), color, thickness)
        cv2.line(result, (0, tripwire_y2), (w, tripwire_y2), color, thickness)

    return result


def get_class_names() -> dict:
    """
    Get standard vehicle class names.

    Returns:
        Dictionary mapping class_id to class name
    """
    return {
        0: "car",
        1: "truck",
        2: "bus",
    }


def get_class_colors() -> dict:
    """
    Get standard colors for vehicle classes.

    Returns:
        Dictionary mapping class_id to BGR color
    """
    return {
        0: (0, 255, 0),    # Green for cars
        1: (255, 0, 0),    # Blue for trucks
        2: (0, 0, 255),    # Red for buses
    }
