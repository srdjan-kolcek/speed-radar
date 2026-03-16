# Dataset Loader Usage Guide

## Overview

The `dataset_loader.py` module provides PyTorch Dataset classes for vehicle detection and lane detection tasks.

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Testing the Loader

```bash
python dataset_loader.py
```

This will:
- Load 3 samples from the training set
- Print statistics (number of vehicles/lanes per image)
- Display visualizations of vehicle bounding boxes and lane polylines

### Vehicle Detection (YOLOv9 Format)

```python
from dataset_loader import VehicleDataset, get_dataloaders

# Create dataset
train_dir = r'C:\SpeedRadar\dataset\train'
vehicle_dataset = VehicleDataset(train_dir, img_size=640)

# Get a single sample
image_tensor, bboxes, img_name = vehicle_dataset[0]
# image_tensor: torch.Tensor [3, 640, 640]
# bboxes: torch.Tensor [N, 5] - [class_id, x_center, y_center, width, height] (normalized)
# img_name: str - image filename

# Create DataLoaders
train_loader, val_loader = get_dataloaders(batch_size=8, dataset_type='vehicle')
```

### Lane Detection (CLRNet Format)

```python
from dataset_loader import LaneDataset, get_dataloaders

# Create dataset
train_dir = r'C:\SpeedRadar\dataset\train'
lane_dataset = LaneDataset(train_dir, img_size=640)

# Get a single sample
image_tensor, lanes, img_name = lane_dataset[0]
# image_tensor: torch.Tensor [3, 640, 640]
# lanes: List[List[List[float]]] - list of polylines with normalized [x, y] coordinates
# img_name: str - image filename

# Create DataLoaders
train_loader, val_loader = get_dataloaders(batch_size=8, dataset_type='lane')
```

### Visualization

```python
from dataset_loader import VehicleDataset, LaneDataset, visualize_sample

# Visualize vehicle detection
vehicle_dataset = VehicleDataset(r'C:\SpeedRadar\dataset\train')
visualize_sample(vehicle_dataset, idx=0, dataset_type='vehicle')

# Visualize lane detection
lane_dataset = LaneDataset(r'C:\SpeedRadar\dataset\train')
visualize_sample(lane_dataset, idx=0, dataset_type='lane')
```

## Dataset Details

### Vehicle Classes

- Class 0: car (red)
- Class 1: truck (green)
- Class 2: bus (blue)

### Lane Filtering

The `LaneDataset` extracts only lanes with:
- `laneDirection`: "parallel"
- `laneStyle`: "dashed"

These are the road lane markings needed for homography calculation.

### Output Format

**VehicleDataset:**
- Bounding boxes in YOLO format: `[class_id, x_center, y_center, width, height]`
- All coordinates normalized to [0, 1] range

**LaneDataset:**
- Polylines as lists of vertices: `[[x1, y1], [x2, y2], ...]`
- Coordinates normalized to [0, 1] range

## Test Results

### Sample Statistics

**Image 1 (000f157f-dab3a407.jpg):**
- Vehicles: 11 (9 cars, 2 buses)
- Lane markings: 2 parallel dashed lanes

**Image 2 (0028cbbf-92f30408.jpg):**
- Vehicles: 8 (6 cars, 2 trucks)
- Lane markings: 6 parallel dashed lanes

**Image 3 (002e6895-442e6bc1.jpg):**
- Vehicles: 6 (6 cars)
- Lane markings: 0 parallel dashed lanes

## File Locations

- Dataset loader: `C:\SpeedRadar\dataset_loader.py`
- Training data: `C:\SpeedRadar\dataset\train\` (4000 images)
- Validation data: `C:\SpeedRadar\dataset\val\` (700 images)
- Requirements: `C:\SpeedRadar\requirements.txt`
