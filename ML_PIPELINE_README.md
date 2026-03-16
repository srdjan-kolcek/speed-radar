# ML Pipeline Architecture

This document describes the modular ML pipeline architecture for the Speed Radar project.

## Overview

The ML pipeline has been refactored from Jupyter notebooks into reusable Python modules, enabling:
- Code reuse across notebooks and backend
- Easier testing and maintenance
- Clear separation of concerns
- Production-ready deployment

## Architecture

```
SpeedRadar/
├── ml_pipeline/              # ML Pipeline Package (NEW)
│   ├── __init__.py
│   ├── vehicle_detector.py  # YOLOv9 detection
│   ├── lane_detector.py     # U-Net lane detection
│   ├── tracker.py           # IoU-based tracking
│   ├── speed_calculator.py  # Homography & speed estimation
│   └── utils.py             # Visualization helpers
│
├── backend/                  # FastAPI Backend (REFACTORED)
│   ├── main.py              # API endpoints
│   ├── config.py            # Configuration
│   ├── models.py            # Pydantic models
│   ├── video_processor.py   # Video processing pipeline
│   ├── requirements.txt     # Dependencies
│   └── README.md            # API documentation
│
├── notebooks/                # Jupyter Notebooks (use ml_pipeline)
│   ├── 01_dataset_exploration.ipynb
│   ├── 02_vehicle_detection_yolov9.ipynb
│   ├── 03_lane_detection_clrnet.ipynb
│   └── 04_speed_estimation.ipynb
│
├── models/weights/           # Trained Model Weights
│   ├── yolov9_vehicle_detection_best.pt
│   └── lane_detector_best.pt
│
└── sample_videos/            # Test Videos
    └── test_video.mp4
```

## ML Pipeline Components

### 1. Vehicle Detector (`ml_pipeline/vehicle_detector.py`)

**Class:** `VehicleDetector`

**Purpose:** Detect vehicles in video frames using YOLOv9.

**Key Methods:**
```python
detector = VehicleDetector(
    model_path="path/to/model.pt",
    confidence_threshold=0.25,
    iou_threshold=0.45
)

# Detect vehicles in a frame
detections = detector.detect(frame)
# Returns: [[x1, y1, x2, y2, confidence, class_id], ...]
```

**Features:**
- YOLOv9 integration via Ultralytics
- Automatic fallback to YOLOv8 if model not found
- Configurable confidence and IoU thresholds
- GPU acceleration support

### 2. Lane Detector (`ml_pipeline/lane_detector.py`)

**Classes:** `SimpleLaneDetector` (model), `LaneDetector` (wrapper)

**Purpose:** Detect lane markings using U-Net with ResNet-18 backbone.

**Key Methods:**
```python
detector = LaneDetector(
    model_path="path/to/model.pt",
    input_size=(640, 640)
)

# Detect lanes in a frame
lane_mask = detector.detect(frame)
# Returns: np.ndarray (H, W) with values 0-1

# Extract polylines from mask
polylines = detector.extract_polylines(lane_mask, threshold=0.5)
# Returns: List of np.ndarray with (x, y) points
```

**Features:**
- U-Net architecture with skip connections
- ResNet-18 encoder for feature extraction
- Binary segmentation output
- Polyline extraction from masks

### 3. Vehicle Tracker (`ml_pipeline/tracker.py`)

**Class:** `VehicleTracker`

**Purpose:** Track vehicles across frames using IoU matching.

**Key Methods:**
```python
tracker = VehicleTracker(
    iou_threshold=0.3,
    max_age=30
)

# Update tracker with new detections
tracked_objects = tracker.update(detections)
# Returns: [[x1, y1, x2, y2, track_id, class_id], ...]
```

**Features:**
- Simple IoU-based matching
- Automatic track creation and deletion
- Configurable track lifetime
- No external dependencies (lightweight)

### 4. Speed Calculator (`ml_pipeline/speed_calculator.py`)

**Class:** `SpeedCalculator`

**Purpose:** Calculate vehicle speeds using homography and tripwire method.

**Key Functions:**
```python
# Calculate homography matrix
warped, homography_matrix = get_homography(image, lane_mask)

# Extract dashed line measurements
p_line, p_gap, best_x = extract_line_segments(warped)

# Calculate scale factor
meters_per_pixel = calculate_meters_per_pixel(p_line, p_gap)

# Initialize speed calculator
calculator = SpeedCalculator(
    tripwire_y1=200,
    tripwire_y2=600,
    fps=30.0
)

# Update with tracked objects
speeds = calculator.update(tracked_objects, homography_matrix, meters_per_pixel)
# Returns: {track_id: speed_kmh}
```

**Features:**
- Perspective transform to bird's-eye view
- Dashed lane marking analysis
- Automatic road type detection (city/highway)
- Tripwire-based speed measurement
- Sanity checks for valid speed ranges

### 5. Utilities (`ml_pipeline/utils.py`)

**Purpose:** Visualization and helper functions.

**Key Functions:**
```python
# Draw detections on image
result = draw_detections(image, detections, class_names)

# Draw tracked objects with speeds
result = draw_tracked_objects(image, tracked_objects, speeds)

# Overlay lane mask
result = draw_lane_mask(image, mask, color=(255, 255, 0))

# Draw tripwires
result = draw_tripwires(image, tripwire_y1, tripwire_y2, homography_matrix)
```

## Usage Examples

### Example 1: Basic Pipeline

```python
from ml_pipeline import (
    VehicleDetector,
    LaneDetector,
    VehicleTracker,
    SpeedCalculator,
    get_homography,
    extract_line_segments,
    calculate_meters_per_pixel,
)

# Initialize components
vehicle_detector = VehicleDetector("models/weights/yolov9_vehicle_detection_best.pt")
lane_detector = LaneDetector("models/weights/lane_detector_best.pt")
tracker = VehicleTracker()
speed_calculator = SpeedCalculator(fps=30)

# Process video
cap = cv2.VideoCapture("video.mp4")
homography_matrix = None
meters_per_pixel = None

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert BGR to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect vehicles
    detections = vehicle_detector.detect(frame_rgb)

    # Track vehicles
    tracked_objects = tracker.update(detections)

    # Detect lanes (every 10 frames)
    if frame_count % 10 == 0:
        lane_mask = lane_detector.detect(frame_rgb)

        if lane_mask is not None:
            # Calculate homography and scale
            warped, M = get_homography(Image.fromarray(frame_rgb), lane_mask)
            if warped is not None and M is not None:
                homography_matrix = M
                p_line, p_gap, _ = extract_line_segments(warped)
                meters_per_pixel = calculate_meters_per_pixel(p_line, p_gap)

    # Calculate speeds
    speeds = speed_calculator.update(tracked_objects, homography_matrix, meters_per_pixel)

    frame_count += 1

cap.release()

# Get results
results = speed_calculator.get_results()
print(f"Detected {len(results)} vehicles with speeds")
```

### Example 2: Using in Jupyter Notebooks

```python
# In your notebook
import sys
sys.path.insert(0, '/path/to/SpeedRadar')

from ml_pipeline import VehicleDetector, draw_detections
import matplotlib.pyplot as plt

# Detect and visualize
detector = VehicleDetector()
detections = detector.detect(image)

result_image = draw_detections(image, detections)
plt.imshow(result_image)
plt.show()
```

### Example 3: FastAPI Backend

The backend uses the ML pipeline through `VideoProcessor`:

```python
# backend/video_processor.py
from ml_pipeline import (
    VehicleDetector,
    LaneDetector,
    VehicleTracker,
    SpeedCalculator,
)

class VideoProcessor:
    def __init__(self):
        self.vehicle_detector = VehicleDetector(...)
        self.lane_detector = LaneDetector(...)

    def process_video(self, video_path):
        # Use ML pipeline components
        tracker = VehicleTracker()
        speed_calculator = SpeedCalculator()

        # Process frames...
        return results
```

## Pipeline Flow

```
Input Video
    ↓
┌─────────────────────────────────────────────┐
│ For Each Frame:                             │
│                                             │
│  1. Vehicle Detection (YOLOv9)              │
│     ↓                                       │
│  2. Vehicle Tracking (IoU Matching)         │
│     ↓                                       │
│  3. Lane Detection (U-Net) [every 10 frames]│
│     ↓                                       │
│  4. Homography Calculation                  │
│     ↓                                       │
│  5. Scale Calculation (dashed lanes)        │
│     ↓                                       │
│  6. Speed Estimation (tripwires)            │
│     ↓                                       │
│  Results: {track_id: speed_kmh}             │
└─────────────────────────────────────────────┘
    ↓
Final Results
```

## Configuration

All parameters can be configured when initializing components:

```python
# Vehicle Detection
detector = VehicleDetector(
    model_path="path/to/model.pt",
    fallback_model="yolov8m.pt",
    confidence_threshold=0.25,  # Min confidence
    iou_threshold=0.45,         # NMS threshold
)

# Lane Detection
lane_detector = LaneDetector(
    model_path="path/to/model.pt",
    input_size=(640, 640),      # Input image size
)

# Tracking
tracker = VehicleTracker(
    iou_threshold=0.3,          # Min IoU for matching
    max_age=30,                 # Max frames to keep track
)

# Speed Calculation
calculator = SpeedCalculator(
    tripwire_y1=200,            # First tripwire (bird's-eye)
    tripwire_y2=600,            # Second tripwire (bird's-eye)
    fps=30.0,                   # Video FPS
    min_valid_speed=20.0,       # Min valid speed (km/h)
    max_valid_speed=150.0,      # Max valid speed (km/h)
)
```

## Dependencies

Core dependencies for the ML pipeline:

```
opencv-python==4.9.0.80      # Computer vision
numpy==1.26.3                # Numerical operations
torch==2.1.2                 # Deep learning framework
torchvision==0.16.2          # Vision models
ultralytics==8.1.0           # YOLO implementation
Pillow==10.2.0               # Image processing
```

Install with:
```bash
pip install -r backend/requirements.txt
```

## Testing

### Unit Testing (Future)

```python
# tests/test_vehicle_detector.py
import pytest
from ml_pipeline import VehicleDetector

def test_vehicle_detector_loads():
    detector = VehicleDetector()
    assert detector.is_loaded()

def test_vehicle_detection():
    detector = VehicleDetector()
    detections = detector.detect(test_image)
    assert len(detections) > 0
    assert len(detections[0]) == 6  # [x1, y1, x2, y2, conf, cls]
```

### Integration Testing

```bash
# Test with sample video
python create_sample_video.py
python -m uvicorn backend.main:app --reload

# Then test API endpoint
curl -X POST "http://localhost:8000/analyze/sample"
```

## Performance Optimization

### GPU Acceleration

Enable GPU for faster processing:

```python
import torch

# Check GPU availability
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Models automatically use GPU if available
detector = VehicleDetector()  # Will use GPU
lane_detector = LaneDetector()  # Will use GPU
```

### Frame Skipping

Process lanes less frequently to save computation:

```python
# In video processing loop
if frame_count % 10 == 0:  # Every 10 frames
    lane_mask = lane_detector.detect(frame)
```

### Batch Processing

Process multiple frames at once (future enhancement):

```python
# Future: Batch inference
detections_batch = vehicle_detector.detect_batch([frame1, frame2, frame3])
```

## Migration Guide

### From Notebooks to ML Pipeline

If you have code in notebooks, migrate it as follows:

**Before (in notebook):**
```python
# Load YOLO model
vehicle_model = YOLO('models/weights/yolov9_vehicle_detection_best.pt')
results = vehicle_model.predict(frame, conf=0.25)

detections = []
for box in results[0].boxes:
    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
    conf = box.conf[0].cpu().numpy()
    cls = int(box.cls[0].cpu().numpy())
    detections.append([x1, y1, x2, y2, conf, cls])
```

**After (using ml_pipeline):**
```python
from ml_pipeline import VehicleDetector

detector = VehicleDetector('models/weights/yolov9_vehicle_detection_best.pt')
detections = detector.detect(frame)
```

## Future Enhancements

1. **ByteTrack Integration**: Replace SimpleTracker with ByteTrack for better tracking
2. **CLRNet Integration**: Use CLRNet instead of simple U-Net for lane detection
3. **Batch Processing**: Support batch inference for faster processing
4. **Multi-GPU Support**: Distribute processing across multiple GPUs
5. **Caching**: Cache homography matrices for similar scenes
6. **Async Processing**: Support asynchronous video processing

## Troubleshooting

### Import Errors

If you get import errors:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ml_pipeline import VehicleDetector
```

### Model Loading Issues

Check model paths:

```python
from pathlib import Path

model_path = Path("models/weights/yolov9_vehicle_detection_best.pt")
assert model_path.exists(), f"Model not found at {model_path}"
```

### Performance Issues

Enable GPU and check CUDA availability:

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"Device count: {torch.cuda.device_count()}")
```

## Contributing

When adding new components to the ML pipeline:

1. Create a new module in `ml_pipeline/`
2. Add class with clear docstrings
3. Export in `ml_pipeline/__init__.py`
4. Update this README with usage examples
5. Add unit tests (future)

## References

- YOLOv9: https://github.com/ultralytics/ultralytics
- U-Net: https://arxiv.org/abs/1505.04597
- ResNet: https://arxiv.org/abs/1512.03385
- Homography: https://docs.opencv.org/master/d9/dab/tutorial_homography.html
