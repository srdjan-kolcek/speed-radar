"""
Create a sample video from validation dataset images.

This script creates a test video for the FastAPI backend by
combining images from the validation dataset.
"""

import cv2
from pathlib import Path

# Configuration
VAL_IMAGES_DIR = Path(r"C:\SpeedRadar\dataset\val\images")
OUTPUT_VIDEO_PATH = Path(r"C:\SpeedRadar\sample_videos\test_video.mp4")
FPS = 30
NUM_IMAGES = 100  # Use first 100 images

def create_sample_video():
    """Create sample video from validation images."""

    # Get image files
    image_files = sorted(list(VAL_IMAGES_DIR.glob("*.jpg")))[:NUM_IMAGES]

    if len(image_files) == 0:
        print(f"ERROR: No images found in {VAL_IMAGES_DIR}")
        return

    print(f"Creating sample video from {len(image_files)} images...")

    # Read first image to get dimensions
    first_img = cv2.imread(str(image_files[0]))
    if first_img is None:
        print(f"ERROR: Could not read first image: {image_files[0]}")
        return

    height, width = first_img.shape[:2]
    print(f"Video dimensions: {width}x{height}")

    # Create output directory
    OUTPUT_VIDEO_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_writer = cv2.VideoWriter(
        str(OUTPUT_VIDEO_PATH),
        fourcc,
        FPS,
        (width, height)
    )

    # Write frames
    for i, img_path in enumerate(image_files):
        img = cv2.imread(str(img_path))
        if img is not None:
            video_writer.write(img)
            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{len(image_files)} images...")
        else:
            print(f"  WARNING: Could not read image: {img_path}")

    video_writer.release()

    print(f"\nSample video created successfully!")
    print(f"Output: {OUTPUT_VIDEO_PATH}")
    print(f"Duration: {len(image_files) / FPS:.2f} seconds")
    print(f"FPS: {FPS}")

if __name__ == "__main__":
    create_sample_video()
