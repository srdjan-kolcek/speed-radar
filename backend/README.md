# Speed Radar Backend API

FastAPI-based REST API for vehicle speed estimation from video footage.

## Overview

This backend provides endpoints for analyzing video files and estimating vehicle speeds using:
- **YOLOv9** for vehicle detection
- **U-Net with ResNet-18** for lane detection
- **IoU-based tracker** for vehicle tracking
- **Homography and tripwire method** for speed calculation

## Architecture

```
backend/
├── main.py              # FastAPI application
├── config.py            # Configuration settings
├── models.py            # Pydantic request/response models
├── video_processor.py   # Video processing logic
├── requirements.txt     # Python dependencies
└── uploads/             # Temporary upload storage
```

The backend imports ML components from the `ml_pipeline` package:
```
ml_pipeline/
├── vehicle_detector.py  # YOLOv9 vehicle detection
├── lane_detector.py     # U-Net lane detection
├── tracker.py           # IoU-based vehicle tracking
├── speed_calculator.py  # Homography and speed estimation
└── utils.py             # Visualization utilities
```

## Setup

### 1. Install Dependencies

```bash
cd C:\SpeedRadar
pip install -r backend/requirements.txt
```

### 2. Verify Model Files

Ensure trained models are in the correct location:
```
models/weights/
├── yolov9_vehicle_detection_best.pt
└── lane_detector_best.pt
```

If models are missing, the API will use fallback models (with reduced accuracy).

### 3. Create Sample Video (Optional)

```bash
python create_sample_video.py
```

This creates a test video at `sample_videos/test_video.mp4` from validation images.

## Running the API

### Development Mode

```bash
cd C:\SpeedRadar
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the built-in runner:

```bash
cd C:\SpeedRadar
python -m backend.main
```

### Production Mode

```bash
cd C:\SpeedRadar
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### General Endpoints

#### `GET /`
Root endpoint with API information.

**Response:**
```json
{
  "name": "Speed Radar API",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "health": "/health",
    "analyze_upload": "/analyze/upload",
    "analyze_sample": "/analyze/sample",
    "docs": "/docs"
  }
}
```

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "message": "All systems operational",
  "models_loaded": true,
  "vehicle_model_path": "C:\\SpeedRadar\\models\\weights\\yolov9_vehicle_detection_best.pt",
  "lane_model_path": "C:\\SpeedRadar\\models\\weights\\lane_detector_best.pt"
}
```

### Analysis Endpoints

#### `POST /analyze/upload`
Upload and analyze a video file.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Video file (MP4, AVI, MOV)
- Max size: 100 MB

**Example (cURL):**
```bash
curl -X POST "http://localhost:8000/analyze/upload" \
  -F "video=@path/to/video.mp4"
```

**Example (Python):**
```python
import requests

url = "http://localhost:8000/analyze/upload"
files = {"video": open("video.mp4", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

**Response:**
```json
{
  "status": "success",
  "processing_time": 12.34,
  "total_frames": 150,
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
    "filename": "video.mp4"
  }
}
```

#### `POST /analyze/sample`
Analyze a preloaded sample video.

**Request:**
- Method: `POST`
- Content-Type: `application/json`
- Body (optional):
```json
{
  "sample_name": "test_video"
}
```

**Example (cURL):**
```bash
curl -X POST "http://localhost:8000/analyze/sample" \
  -H "Content-Type: application/json" \
  -d '{"sample_name": "test_video"}'
```

**Example (Python):**
```python
import requests

url = "http://localhost:8000/analyze/sample"
data = {"sample_name": "test_video"}
response = requests.post(url, json=data)
print(response.json())
```

**Response:**
```json
{
  "status": "success",
  "processing_time": 8.56,
  "total_frames": 100,
  "results": [
    {
      "track_id": 1,
      "speed_kmh": 48.3,
      "confidence": 0.87,
      "vehicle_type": "car"
    }
  ],
  "metadata": {
    "fps": 30.0,
    "sample_name": "test_video"
  }
}
```

#### `GET /samples/list`
List available sample videos.

**Response:**
```json
{
  "samples": ["test_video", "highway_scene"]
}
```

## Configuration

Configuration is managed in `backend/config.py`:

### Model Settings
```python
VEHICLE_MODEL_PATH = MODELS_DIR / "yolov9_vehicle_detection_best.pt"
LANE_MODEL_PATH = MODELS_DIR / "lane_detector_best.pt"
FALLBACK_VEHICLE_MODEL = "yolov8m.pt"
```

### Detection Parameters
```python
MIN_CONFIDENCE = 0.25      # Minimum confidence for vehicle detection
IOU_THRESHOLD = 0.45       # IoU threshold for NMS
TRACKER_IOU_THRESHOLD = 0.3  # IoU threshold for tracking
TRACKER_MAX_AGE = 30       # Maximum frames to keep lost track
```

### Speed Calculation
```python
TRIPWIRE_Y1 = 200         # First tripwire (bird's-eye view)
TRIPWIRE_Y2 = 600         # Second tripwire (bird's-eye view)
MIN_VALID_SPEED_KMH = 20  # Minimum valid speed
MAX_VALID_SPEED_KMH = 150 # Maximum valid speed
```

### API Settings
```python
MAX_VIDEO_SIZE_MB = 100
ALLOWED_VIDEO_FORMATS = [".mp4", ".avi", ".mov"]
ALLOWED_ORIGINS = ["*"]  # CORS origins
```

## Response Models

### SpeedResult
```python
{
  "track_id": int,        # Unique tracking ID
  "speed_kmh": float,     # Estimated speed in km/h
  "confidence": float,    # Confidence score (0.0-1.0)
  "vehicle_type": str     # Vehicle type (car/truck/bus)
}
```

### AnalysisResponse
```python
{
  "status": str,                    # success/error
  "processing_time": float,         # Processing time in seconds
  "total_frames": int,              # Total frames processed
  "results": List[SpeedResult],     # Speed measurements
  "error": Optional[str],           # Error message if failed
  "metadata": Optional[dict]        # Additional metadata
}
```

## Error Handling

The API returns appropriate HTTP status codes:

- **200 OK**: Request successful
- **400 Bad Request**: Invalid request parameters
- **404 Not Found**: Sample video not found
- **413 Payload Too Large**: Video file too large
- **500 Internal Server Error**: Processing error
- **503 Service Unavailable**: Models not initialized

Example error response:
```json
{
  "detail": "File too large: 150.23MB (max: 100MB)"
}
```

## Performance Considerations

### Processing Time
- Depends on video length, resolution, and hardware
- GPU acceleration recommended for faster processing
- Typical: 2-5 seconds per second of video on GPU

### Optimization Tips
1. **Use GPU**: Install CUDA-enabled PyTorch
2. **Reduce Resolution**: Process at lower resolution if acceptable
3. **Batch Processing**: Process multiple videos in parallel
4. **Lane Detection**: Already optimized to run every 10 frames

### Resource Requirements
- **CPU**: Multi-core processor recommended
- **RAM**: 8GB minimum, 16GB recommended
- **GPU**: NVIDIA GPU with 4GB+ VRAM (optional but recommended)
- **Storage**: ~5GB for models and temporary files

## Integration Examples

### React Native / Mobile App

```javascript
const analyzeVideo = async (videoUri) => {
  const formData = new FormData();
  formData.append('video', {
    uri: videoUri,
    type: 'video/mp4',
    name: 'upload.mp4',
  });

  try {
    const response = await fetch('http://localhost:8000/analyze/upload', {
      method: 'POST',
      body: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    const data = await response.json();
    console.log('Speed results:', data.results);
  } catch (error) {
    console.error('Error:', error);
  }
};
```

### Python Client

```python
import requests
from pathlib import Path

class SpeedRadarClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def analyze_video(self, video_path):
        """Upload and analyze a video file."""
        url = f"{self.base_url}/analyze/upload"
        with open(video_path, "rb") as f:
            files = {"video": f}
            response = requests.post(url, files=files)
            response.raise_for_status()
            return response.json()

    def analyze_sample(self, sample_name="test_video"):
        """Analyze a sample video."""
        url = f"{self.base_url}/analyze/sample"
        data = {"sample_name": sample_name}
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def health_check(self):
        """Check API health."""
        url = f"{self.base_url}/health"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

# Usage
client = SpeedRadarClient()
results = client.analyze_video("path/to/video.mp4")
print(f"Detected {len(results['results'])} vehicles")
```

## Troubleshooting

### Models Not Loading
- Check that model files exist at the specified paths
- Verify file permissions
- Check logs for detailed error messages

### Low Accuracy
- Ensure trained models are used (not fallback models)
- Check that video quality is sufficient
- Verify camera angle is compatible with homography calculation

### Slow Processing
- Enable GPU acceleration
- Reduce video resolution
- Process shorter video clips
- Increase `TRIPWIRE_Y1/Y2` interval for faster speed calculations

### CORS Errors
- Update `ALLOWED_ORIGINS` in `config.py`
- Restart the API after configuration changes

## Development

### Adding New Endpoints

1. Define request/response models in `models.py`
2. Add endpoint in `main.py`
3. Update this README with documentation

### Testing

```bash
# Interactive API docs
http://localhost:8000/docs

# Manual testing with cURL
curl -X POST "http://localhost:8000/analyze/sample"

# Python unit tests (if implemented)
pytest tests/
```

## License

MIT License - See project root for details.

## Support

For issues and questions:
- Check the logs for error details
- Review the interactive API docs at `/docs`
- Consult the main project README
