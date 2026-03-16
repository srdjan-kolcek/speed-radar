# Speed Radar ML Pipeline

This directory contains the complete machine learning pipeline for car speed detection using computer vision.

## Pipeline Overview

The system detects vehicles, tracks them across frames, detects lane markings, and estimates vehicle speeds using homography and scale calibration.

## Notebooks (Execute in Order)

### 1. `01_dataset_exploration.ipynb`
**Purpose:** Explore and analyze the dataset

**Contents:**
- Load train/val datasets (4000 train, 700 val images)
- Display dataset statistics (total samples, class distribution)
- Visualize samples with vehicle bboxes (car, truck, bus)
- Visualize samples with lane markings (parallel dashed lines)
- Show distribution of vehicles per image
- Show distribution of lane markings per image

**Output:** Dataset statistics and visualizations

---

### 2. `02_vehicle_detection_yolov9.ipynb`
**Purpose:** Train YOLOv9 model for vehicle detection

**Contents:**
1. **Setup:** Install Ultralytics YOLO
2. **Data Preparation:** Convert dataset to YOLO format (txt labels)
3. **Model Configuration:**
   - Model: YOLOv9-C (or YOLOv8m fallback)
   - Classes: 3 (car, truck, bus)
   - Input size: 640x640
4. **Training:**
   - Epochs: 50 (configurable)
   - Batch size: 16
   - Learning rate: 0.01 with cosine decay
   - Optimizer: SGD
5. **Evaluation:**
   - mAP@0.5 and mAP@0.5:0.95
   - Per-class metrics
   - Visualize predictions on validation set
6. **Model Saving:** `C:\SpeedRadar\models\weights\yolov9_vehicle_detection_best.pt`

**Output:** Trained vehicle detection model

---

### 3. `03_lane_detection_clrnet.ipynb`
**Purpose:** Train lane detection model for parallel dashed lanes

**Contents:**
1. **Setup:** Install dependencies
2. **Data Preparation:** Convert to TuSimple-like format
3. **Model Architecture:**
   - U-Net with ResNet-18 backbone
   - Segmentation-based approach
   - Input size: 640x640
4. **Training:**
   - Epochs: 30 (with early stopping)
   - Batch size: 8
   - Optimizer: AdamW
   - Learning rate: 0.0001
   - Loss: Binary Cross Entropy
5. **Lane Extraction:** Convert segmentation masks to polylines
6. **Model Saving:** `C:\SpeedRadar\models\weights\lane_detector_best.pt`

**Output:** Trained lane detection model

---

### 4. `04_speed_estimation.ipynb`
**Purpose:** Complete speed estimation pipeline

**Contents:**
1. **Load Models:**
   - Vehicle detector (YOLOv9)
   - Lane detector (U-Net)
2. **Homography & Scale Calculation:**
   - `get_homography()`: Transform to bird's-eye view
   - `extract_line_segments()`: Detect dashed lane patterns
   - `calculate_meters_per_pixel()`: Calibrate scale from lane markings
3. **Vehicle Tracking:**
   - Simple IoU-based tracker
   - Assigns unique track IDs to vehicles
4. **Speed Estimation:**
   - Place virtual tripwires in bird's-eye view
   - Track when vehicles cross tripwires
   - Calculate: `speed = distance / time × 3.6` (km/h)
5. **Pipeline Integration:**
   ```
   Frame → Vehicle Detection → Lane Detection → Tracking
   → Homography → Scale Calculation → Speed Estimation
   ```
6. **Output Format:**
   ```json
   [
     {"track_id": 1, "speed_kmh": 45.3, "frame": 42, "confidence": 0.85},
     {"track_id": 2, "speed_kmh": 52.1, "frame": 58, "confidence": 0.92}
   ]
   ```

**Output:**
- Speed estimations JSON: `C:\SpeedRadar\speed_estimations.json`
- Test video: `C:\SpeedRadar\test_video.mp4`

---

## Directory Structure

```
C:\SpeedRadar\
├── dataset\
│   ├── train\
│   │   ├── images\  (4000 images)
│   │   └── labels\  (JSON annotations)
│   └── val\
│       ├── images\  (700 images)
│       └── labels\  (JSON annotations)
├── models\
│   ├── weights\
│   │   ├── yolov9_vehicle_detection_best.pt
│   │   ├── lane_detector_best.pt
│   │   └── lane_detector_complete.pt
│   └── car_and_road_recognition_model.ipynb  (reference)
├── dataset_loader.py  (Dataset classes)
├── 01_dataset_exploration.ipynb
├── 02_vehicle_detection_yolov9.ipynb
├── 03_lane_detection_clrnet.ipynb
├── 04_speed_estimation.ipynb
├── speed_estimations.json  (output)
└── test_video.mp4  (output)
```

---

## Key Functions (from Notebook 4)

### Homography and Scale Calculation
```python
get_homography(image, mask)
# Transforms image to bird's-eye view using road mask

extract_line_segments(warped_img)
# Detects dashed lane pattern and measures line/gap pixels

calculate_meters_per_pixel(p_line, p_gap)
# Calibrates scale: 3m lines, 1m or 3m gaps
```

### Speed Estimation
```python
SpeedCalculator.update(tracked_objects, homography, scale)
# Tracks vehicles crossing tripwires
# Calculates: distance (meters) / time (seconds) = speed (m/s)
# Converts to km/h: speed_ms × 3.6
```

---

## Running the Pipeline

### Option 1: Execute All Notebooks Sequentially
1. Open each notebook in Jupyter/VS Code
2. Run all cells in order (01 → 02 → 03 → 04)
3. Training notebooks (02, 03) will take time depending on GPU

### Option 2: Skip Training (Use Pre-trained Models)
If you already have trained models:
1. Run notebook 01 for data exploration
2. Skip to notebook 04 for speed estimation
3. Ensure model weights exist in `C:\SpeedRadar\models\weights\`

---

## Expected Results

### Validation Metrics (Notebook 02 - Vehicle Detection)
- **mAP@0.5:** ~0.70-0.85
- **mAP@0.5:0.95:** ~0.45-0.65
- **Classes:** car (highest), truck, bus

### Validation Metrics (Notebook 03 - Lane Detection)
- **Validation Loss:** <0.1 (after training)
- **Lane detection rate:** Depends on dataset (many images may not have parallel dashed lanes)

### Speed Estimation (Notebook 04)
- **Expected range:** 30-80 km/h for city streets
- **Accuracy:** Depends on:
  - Lane detection quality
  - Homography accuracy
  - Camera calibration
  - Tripwire positioning

---

## Troubleshooting

### Issue: Vehicle detector not found
**Solution:** Check if `C:\SpeedRadar\models\weights\yolov9_vehicle_detection_best.pt` exists. If not, run notebook 02 first.

### Issue: Lane detector not found
**Solution:** Check if `C:\SpeedRadar\models\weights\lane_detector_best.pt` exists. If not, run notebook 03 first.

### Issue: No speed measurements
**Possible causes:**
1. Lane detection failed (no parallel dashed lanes in images)
2. Vehicles didn't cross both tripwires
3. Homography calculation failed
4. Scale calculation failed

**Solutions:**
- Check lane detection visualizations
- Adjust tripwire positions in `SpeedCalculator`
- Verify dashed lane markings are visible in test images

### Issue: Unrealistic speeds
**Possible causes:**
- Incorrect scale calibration
- Wrong lane type detection
- Poor homography matrix

**Solutions:**
- Manually verify `meters_per_pixel` calculation
- Check if lane type (city vs. open road) is correct
- Visualize warped bird's-eye view image

---

## Hardware Requirements

### Minimum:
- **CPU:** 4+ cores
- **RAM:** 8GB
- **GPU:** Optional (CPU training is slow)

### Recommended:
- **CPU:** 8+ cores
- **RAM:** 16GB
- **GPU:** NVIDIA GPU with 6GB+ VRAM (for faster training)
- **Storage:** 10GB free space

---

## Dependencies

All dependencies are installed within the notebooks using pip:
- ultralytics (YOLO)
- torch, torchvision
- opencv-python-headless
- pillow
- matplotlib
- numpy
- scipy
- scikit-learn

---

## Citation

If using the BDD100K dataset:
```
@inproceedings{bdd100k,
    author = {Yu, Fisher and Chen, Haofeng and Wang, Xin and Xian, Wenqi and Chen, Yingying and Liu, Fangchen and Madhavan, Vashisht and Darrell, Trevor},
    title = {BDD100K: A Diverse Driving Dataset for Heterogeneous Multitask Learning},
    booktitle = {IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
    year = {2020}
}
```

---

## License

This pipeline is provided for educational and research purposes.

---

## Contact

For questions or issues, refer to the individual notebook documentation or check the console output for error messages.
