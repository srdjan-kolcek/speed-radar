# Quick Start Guide - Speed Radar API

## Setup (5 minutes)

### 1. Install Dependencies

```bash
cd C:\SpeedRadar
pip install -r backend/requirements.txt
```

### 2. Verify Models

Check that trained models exist:
```bash
dir models\weights\yolov9_vehicle_detection_best.pt
dir models\weights\lane_detector_best.pt
```

If models are missing, the API will use fallback models (with reduced accuracy).

### 3. Create Sample Video (Optional)

```bash
python create_sample_video.py
```

This creates `sample_videos/test_video.mp4` from validation images.

## Running the API

### Start Server

```bash
cd C:\SpeedRadar
python -m uvicorn backend.main:app --reload
```

The API will start at: **http://localhost:8000**

### Interactive Documentation

Open in browser: **http://localhost:8000/docs**

## Test the API

### Option 1: Using Sample Video

```bash
curl -X POST "http://localhost:8000/analyze/sample"
```

### Option 2: Upload Your Own Video

```bash
curl -X POST "http://localhost:8000/analyze/upload" \
  -F "video=@path/to/your/video.mp4"
```

### Option 3: Python Client

```python
import requests

# Analyze sample video
response = requests.post("http://localhost:8000/analyze/sample")
results = response.json()

print(f"Status: {results['status']}")
print(f"Processing time: {results['processing_time']:.2f}s")
print(f"Vehicles detected: {len(results['results'])}")

for vehicle in results['results']:
    print(f"  - Vehicle {vehicle['track_id']}: {vehicle['speed_kmh']:.1f} km/h ({vehicle['vehicle_type']})")
```

## Expected Output

```json
{
  "status": "success",
  "processing_time": 8.56,
  "total_frames": 100,
  "results": [
    {
      "track_id": 1,
      "speed_kmh": 45.2,
      "confidence": 0.89,
      "vehicle_type": "car"
    },
    {
      "track_id": 2,
      "speed_kmh": 52.7,
      "confidence": 0.92,
      "vehicle_type": "truck"
    }
  ],
  "metadata": {
    "fps": 30.0,
    "sample_name": "test_video"
  }
}
```

## Using ML Pipeline in Notebooks

```python
# Add to your notebook
import sys
sys.path.insert(0, r'C:\SpeedRadar')

from ml_pipeline import VehicleDetector, LaneDetector
import cv2
import matplotlib.pyplot as plt

# Load models
vehicle_detector = VehicleDetector()
lane_detector = LaneDetector()

# Detect vehicles
image = cv2.imread('test_image.jpg')
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

detections = vehicle_detector.detect(image_rgb)
print(f"Detected {len(detections)} vehicles")

# Detect lanes
lane_mask = lane_detector.detect(image_rgb)
plt.imshow(lane_mask, cmap='gray')
plt.show()
```

## Troubleshooting

### Port Already in Use

```bash
# Use a different port
python -m uvicorn backend.main:app --reload --port 8001
```

### Models Not Found

Check paths in `backend/config.py`:
```python
VEHICLE_MODEL_PATH = MODELS_DIR / "yolov9_vehicle_detection_best.pt"
LANE_MODEL_PATH = MODELS_DIR / "lane_detector_best.pt"
```

### Import Errors

Make sure you're in the correct directory:
```bash
cd C:\SpeedRadar
python -m uvicorn backend.main:app --reload
```

## Documentation

- **API Documentation**: `backend/README.md`
- **ML Pipeline Architecture**: `ML_PIPELINE_README.md`
- **Refactoring Summary**: `REFACTORING_SUMMARY.md`
- **Interactive Docs**: http://localhost:8000/docs (when server is running)

## Next Steps

1. Read `backend/README.md` for detailed API documentation
2. Read `ML_PIPELINE_README.md` for ML architecture details
3. Explore the interactive API docs at `/docs`
4. Try uploading your own videos
5. Integrate with your mobile app or frontend

## Support

For issues:
1. Check the server logs
2. Review the documentation
3. Test with the sample video first
4. Verify model files exist
