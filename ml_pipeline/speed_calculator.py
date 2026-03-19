"""
Speed Calculation Module - Homography and Speed Estimation

Extracted from notebooks: car_and_road_recognition_model.ipynb and 04_speed_estimation.ipynb
"""

import logging
from collections import defaultdict
from typing import List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


def get_homography(
    original_image_pil: Image.Image,
    model_mask_640: np.ndarray
) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """
    Calculate homography matrix to transform image to bird's-eye view.

    Args:
        original_image_pil: Original image as PIL Image
        model_mask_640: Lane segmentation mask (640x640)

    Returns:
        Tuple of (warped_image, homography_matrix) or (None, None) if calculation fails
    """
    orig_w, orig_h = original_image_pil.size
    full_mask = cv2.resize(
        model_mask_640, (orig_w, orig_h), interpolation=cv2.INTER_NEAREST
    )

    # Find all pixels of the mask
    all_y, all_x = np.where(full_mask > 0.5)

    if len(all_x) == 0 or len(all_y) == 0:
        return None, None

    # Calculate the range of x and y axis
    delta_x = np.max(all_x) - np.min(all_x)
    delta_y = np.max(all_y) - np.min(all_y)

    # If delta_x is significantly larger, we treat it as horizontal
    if delta_x > 1.2 * delta_y:
        # Horizontal roads, we take dots on the left and right side
        offset_x = int(delta_x * 0.1)
        left_x = np.min(all_x) + offset_x
        right_x = np.max(all_x) - offset_x

        # Edges of the road are on the top and bottom of that x
        left_indices = np.where(full_mask[:, left_x] > 0.5)[0]
        right_indices = np.where(full_mask[:, right_x] > 0.5)[0]

        if len(left_indices) == 0 or len(right_indices) == 0:
            return None, None

        # Ordering points for 400x800 vertical output
        src_pts = np.float32([
            [left_x, left_indices[0]],
            [right_x, right_indices[0]],
            [right_x, right_indices[-1]],
            [left_x, left_indices[-1]],
        ])
    else:
        # Vertical road
        top_y = np.min(all_y) + 30
        bottom_y = np.max(all_y) - 20
        top_indices = np.where(full_mask[top_y, :] > 0.5)[0]
        bottom_indices = np.where(full_mask[bottom_y, :] > 0.5)[0]

        if len(top_indices) == 0 or len(bottom_indices) == 0:
            return None, None

        src_pts = np.float32([
            [top_indices[0], top_y],
            [top_indices[-1], top_y],
            [bottom_indices[-1], bottom_y],
            [bottom_indices[0], bottom_y],
        ])

    # Transform to bird's eye view
    dst_pts = np.float32([[0, 0], [400, 0], [400, 800], [0, 800]])
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(np.array(original_image_pil), M, (400, 800))

    return warped, M


def extract_line_segments(
    warped_img: np.ndarray
) -> Tuple[Optional[int], Optional[int], int]:
    """
    Extract line segments from warped bird's-eye view image.

    This function analyzes dashed lane markings to find line and gap measurements.

    Args:
        warped_img: Warped bird's-eye view image (RGB)

    Returns:
        Tuple of (p_line, p_gap, best_x) where:
        - p_line: Length of dashed line in pixels
        - p_gap: Length of gap between dashes in pixels
        - best_x: X coordinate where measurement was taken
    """
    # Grayscale the image
    gray = cv2.cvtColor(warped_img, cv2.COLOR_RGB2GRAY)
    # Otsu threshold for extracting lines
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    height, width = thresh.shape

    # Find the best x axis by looking for dashed lines
    best_x = width // 2
    max_score = 0
    best_segments = []

    # Scan from left to right, staying away from sidewalk edges
    for x in range(50, width - 50, 10):
        # Create the tunnel around current x
        sample_width = 5
        tunnel = thresh[:, max(0, x - sample_width): min(width, x + sample_width)]

        # Average of the tunnel to boolean
        line_map = np.mean(tunnel, axis=1) > 127

        # Group into segments
        segments = []
        if len(line_map) > 0:
            count = 1
            for i in range(1, len(line_map)):
                if line_map[i] == line_map[i - 1]:
                    count += 1
                else:
                    segments.append((line_map[i - 1], count))
                    count = 1
            segments.append((line_map[-1], count))

            # Score to avoid tram rails or long curbs
            transitions = len(segments)
            score = transitions

            for is_white, length in segments:
                # If the white line is too long (>40% of height), it's probably a rail
                if is_white and length > (height * 0.4):
                    score = 0
                    break

            # Take the x with best score
            if score > max_score:
                max_score = score
                best_x = x
                best_segments = segments

    if not best_segments:
        logger.debug("extract_line_segments: No segments found at all")
        return None, None, best_x

    # Log what we found so we can diagnose filtering issues
    logger.debug(f"extract_line_segments: best_x={best_x}, max_score={max_score}, "
                 f"num_segments={len(best_segments)}")
    logger.debug(f"extract_line_segments: segments (is_white, length): "
                 f"{[(bool(s[0]), s[1]) for s in best_segments[:10]]}")

    # Find the first valid couple
    p_line, p_gap = None, None
    for i in range(len(best_segments) - 1):
        is_white = best_segments[i][0]
        w_len = best_segments[i][1]
        g_len = best_segments[i + 1][1]
        is_gap_dark = not best_segments[i + 1][0]

        # Use a safe range for lines (30px to 300px)
        # NOTE: Must use == True, not 'is True', because segment values
        # are numpy.bool_ which fails identity comparison with Python bool
        if is_white == True and 30 < w_len < 300:
            if is_gap_dark and 20 < g_len < 400:
                p_line = w_len
                p_gap = g_len
                break
            else:
                logger.debug(f"extract_line_segments: white seg {w_len}px OK, "
                             f"but next seg (dark={is_gap_dark}, len={g_len}) "
                             f"failed gap filter (need 20 < gap < 400)")
        elif is_white == True:
            logger.debug(f"extract_line_segments: white seg {w_len}px "
                         f"failed line filter (need 30 < line < 300)")

    if p_line is None:
        logger.debug("extract_line_segments: No valid line-gap pair found in segments")

    return p_line, p_gap, best_x


def calculate_meters_per_pixel(
    p_line: Optional[int],
    p_gap: Optional[int],
    verbose: bool = False
) -> Optional[float]:
    """
    Calculate scale factor (meters per pixel) from dashed lane markings.

    Uses standard lane marking dimensions:
    - City roads: 3m line, 1m gap
    - Open roads: 3m line, 3m gap

    Args:
        p_line: Length of dashed line in pixels
        p_gap: Length of gap between dashes in pixels
        verbose: Whether to log detailed information

    Returns:
        Scale factor in meters per pixel, or None if calculation fails
    """
    if p_line is None or p_gap is None:
        if verbose:
            logger.warning("System did not detect a clear line-gap pair.")
        return None

    ratio = p_line / p_gap

    # If the line is a lot bigger than the gap, we say it's 3m line and 1m gap
    if ratio >= 2.0:
        road_type = "City road (3m line, 1m gap)"
        meters_per_pixel = 3.0 / p_line
    else:
        road_type = "Open road (3m line, 3m gap)"
        meters_per_pixel = 3.0 / p_line

    # Safety check
    if meters_per_pixel > 0.5:
        if verbose:
            logger.warning("Warning: Scale factor is suspiciously large!")
        return None

    if verbose:
        logger.info(f"Road type: {road_type}")
        logger.info(f"Pixels: Line={p_line}px, Gap={p_gap}px (Ratio: {ratio:.2f})")
        logger.info(f"Final scale: {meters_per_pixel:.5f} meters per pixel")

    return meters_per_pixel
