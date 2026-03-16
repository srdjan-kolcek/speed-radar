"""
Dataset Loader for Vehicle Detection and Lane Detection
Supports YOLOv9 (vehicle detection) and CLRNet (lane detection)
"""

import os
import json
import torch
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import torchvision.transforms as transforms
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches


# Class mapping for vehicle detection
VEHICLE_CLASSES = {
    "car": 0,
    "truck": 1,
    "bus": 2
}

CLASS_NAMES = {0: "car", 1: "truck", 2: "bus"}


def load_json_label(json_path):
    """
    Parse JSON annotation file.

    Args:
        json_path: Path to JSON file

    Returns:
        Dictionary containing parsed JSON data
    """
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data


class VehicleDataset(Dataset):
    """
    Dataset for vehicle detection (YOLOv9 format).
    Extracts car/truck/bus bounding boxes and converts to YOLO format.
    """

    def __init__(self, root_dir, img_size=640, transform=None):
        """
        Args:
            root_dir: Root directory containing 'images/' and 'labels/'
            img_size: Target image size (default: 640)
            transform: Optional custom transforms
        """
        self.root_dir = root_dir
        self.img_dir = os.path.join(root_dir, 'images')
        self.label_dir = os.path.join(root_dir, 'labels')
        self.img_size = img_size

        # Get all image files
        self.image_files = sorted([f for f in os.listdir(self.img_dir) if f.endswith('.jpg')])

        # Default transform: resize and convert to tensor
        if transform is None:
            self.transform = transforms.Compose([
                transforms.Resize((img_size, img_size)),
                transforms.ToTensor(),
            ])
        else:
            self.transform = transform

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        # Load image
        img_name = self.image_files[idx]
        img_path = os.path.join(self.img_dir, img_name)
        image = Image.open(img_path).convert('RGB')

        # Get original dimensions
        orig_w, orig_h = image.size

        # Load corresponding JSON label
        json_name = img_name.replace('.jpg', '.json')
        json_path = os.path.join(self.label_dir, json_name)
        label_data = load_json_label(json_path)

        # Extract vehicle bounding boxes
        vehicles = []
        if label_data['frames']:
            frame = label_data['frames'][0]
            for obj in frame['objects']:
                category = obj.get('category', '')
                if category in VEHICLE_CLASSES and 'box2d' in obj:
                    box = obj['box2d']
                    class_id = VEHICLE_CLASSES[category]

                    # Original coordinates
                    x1, y1 = box['x1'], box['y1']
                    x2, y2 = box['x2'], box['y2']

                    # Convert to YOLO format: [class_id, x_center, y_center, width, height]
                    # Normalized by original image dimensions
                    x_center = ((x1 + x2) / 2) / orig_w
                    y_center = ((y1 + y2) / 2) / orig_h
                    width = (x2 - x1) / orig_w
                    height = (y2 - y1) / orig_h

                    vehicles.append([class_id, x_center, y_center, width, height])

        # Convert to tensor
        if len(vehicles) > 0:
            bboxes = torch.tensor(vehicles, dtype=torch.float32)
        else:
            bboxes = torch.zeros((0, 5), dtype=torch.float32)

        # Apply transform to image
        image_tensor = self.transform(image)

        return image_tensor, bboxes, img_name


class LaneDataset(Dataset):
    """
    Dataset for lane detection (CLRNet format).
    Extracts lane markings with parallel direction and dashed style.
    """

    def __init__(self, root_dir, img_size=640, transform=None):
        """
        Args:
            root_dir: Root directory containing 'images/' and 'labels/'
            img_size: Target image size (default: 640)
            transform: Optional custom transforms
        """
        self.root_dir = root_dir
        self.img_dir = os.path.join(root_dir, 'images')
        self.label_dir = os.path.join(root_dir, 'labels')
        self.img_size = img_size

        # Get all image files
        self.image_files = sorted([f for f in os.listdir(self.img_dir) if f.endswith('.jpg')])

        # Default transform: resize and convert to tensor
        if transform is None:
            self.transform = transforms.Compose([
                transforms.Resize((img_size, img_size)),
                transforms.ToTensor(),
            ])
        else:
            self.transform = transform

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        # Load image
        img_name = self.image_files[idx]
        img_path = os.path.join(self.img_dir, img_name)
        image = Image.open(img_path).convert('RGB')

        # Get original dimensions
        orig_w, orig_h = image.size

        # Load corresponding JSON label
        json_name = img_name.replace('.jpg', '.json')
        json_path = os.path.join(self.label_dir, json_name)
        label_data = load_json_label(json_path)

        # Extract lane polylines (parallel + dashed)
        lanes = []
        if label_data['frames']:
            frame = label_data['frames'][0]
            for obj in frame['objects']:
                category = obj.get('category', '')

                # Check for newer format with 'lane' category and poly2d
                if category == 'lane' and 'poly2d' in obj and 'attributes' in obj:
                    attrs = obj['attributes']
                    lane_direction = attrs.get('laneDirection', '')
                    lane_style = attrs.get('laneStyle', '')

                    # Filter: parallel direction and dashed style
                    if lane_direction == 'parallel' and lane_style == 'dashed':
                        for poly in obj['poly2d']:
                            vertices = poly.get('vertices', [])
                            if vertices:
                                # Normalize coordinates
                                normalized_vertices = []
                                for vertex in vertices:
                                    x_norm = vertex[0] / orig_w
                                    y_norm = vertex[1] / orig_h
                                    normalized_vertices.append([x_norm, y_norm])
                                lanes.append(normalized_vertices)

        # Apply transform to image
        image_tensor = self.transform(image)

        return image_tensor, lanes, img_name


def visualize_sample(dataset, idx, dataset_type='vehicle'):
    """
    Visualize a sample from the dataset with annotations.

    Args:
        dataset: VehicleDataset or LaneDataset instance
        idx: Sample index
        dataset_type: 'vehicle' or 'lane'
    """
    if dataset_type == 'vehicle':
        image_tensor, bboxes, img_name = dataset[idx]
    else:
        image_tensor, lanes, img_name = dataset[idx]

    # Convert tensor to numpy for visualization
    image_np = image_tensor.permute(1, 2, 0).numpy()

    # Create figure
    fig, ax = plt.subplots(1, figsize=(12, 8))
    ax.imshow(image_np)
    ax.set_title(f'{dataset_type.capitalize()} Dataset - {img_name}')

    img_h, img_w = image_np.shape[:2]

    if dataset_type == 'vehicle':
        # Draw bounding boxes
        colors = ['red', 'green', 'blue']
        for bbox in bboxes:
            class_id, x_center, y_center, width, height = bbox
            class_id = int(class_id)

            # Convert from YOLO format to pixel coordinates
            x1 = (x_center - width / 2) * img_w
            y1 = (y_center - height / 2) * img_h
            w = width * img_w
            h = height * img_h

            # Draw rectangle
            rect = patches.Rectangle(
                (x1, y1), w, h,
                linewidth=2,
                edgecolor=colors[class_id],
                facecolor='none'
            )
            ax.add_patch(rect)

            # Add label
            ax.text(
                x1, y1 - 5,
                CLASS_NAMES[class_id],
                color=colors[class_id],
                fontsize=10,
                weight='bold',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1)
            )

        ax.set_xlabel(f'Total vehicles: {len(bboxes)}')

    else:  # lane
        # Draw lane polylines
        for lane in lanes:
            lane_array = np.array(lane)
            # Convert normalized coordinates to pixels
            lane_pixels = lane_array * [img_w, img_h]

            # Draw polyline
            ax.plot(
                lane_pixels[:, 0],
                lane_pixels[:, 1],
                'y-',
                linewidth=3,
                marker='o',
                markersize=5
            )

        ax.set_xlabel(f'Total lane markings: {len(lanes)}')

    ax.axis('off')
    plt.tight_layout()
    plt.show()


def get_dataloaders(batch_size=8, img_size=640, dataset_type='vehicle'):
    """
    Create train and validation DataLoaders.

    Args:
        batch_size: Batch size for DataLoader
        img_size: Image size (default: 640)
        dataset_type: 'vehicle' or 'lane'

    Returns:
        train_loader, val_loader
    """
    train_dir = r'C:\SpeedRadar\dataset\train'
    val_dir = r'C:\SpeedRadar\dataset\val'

    if dataset_type == 'vehicle':
        train_dataset = VehicleDataset(train_dir, img_size=img_size)
        val_dataset = VehicleDataset(val_dir, img_size=img_size)
    else:
        train_dataset = LaneDataset(train_dir, img_size=img_size)
        val_dataset = LaneDataset(val_dir, img_size=img_size)

    # Custom collate function for variable-length outputs
    def collate_fn(batch):
        images = torch.stack([item[0] for item in batch])
        targets = [item[1] for item in batch]
        names = [item[2] for item in batch]
        return images, targets, names

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=collate_fn,
        num_workers=0  # Set to 0 for Windows compatibility
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=collate_fn,
        num_workers=0
    )

    return train_loader, val_loader


# ============================================================================
# TEST SECTION
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("Testing Dataset Loaders")
    print("=" * 70)

    # Test VehicleDataset
    print("\n[1/3] Testing VehicleDataset...")
    train_dir = r'C:\SpeedRadar\dataset\train'
    vehicle_dataset = VehicleDataset(train_dir, img_size=640)

    print(f"Total training samples: {len(vehicle_dataset)}")

    # Load 3 samples and print statistics
    print("\nSample statistics (first 3 images):")
    for i in range(3):
        image_tensor, bboxes, img_name = vehicle_dataset[i]
        num_vehicles = len(bboxes)

        # Count by class
        class_counts = {name: 0 for name in CLASS_NAMES.values()}
        for bbox in bboxes:
            class_id = int(bbox[0])
            class_counts[CLASS_NAMES[class_id]] += 1

        print(f"\n  Sample {i+1}: {img_name}")
        print(f"    Image shape: {image_tensor.shape}")
        print(f"    Total vehicles: {num_vehicles}")
        print(f"    Class breakdown: {class_counts}")

    # Test LaneDataset
    print("\n" + "=" * 70)
    print("[2/3] Testing LaneDataset...")
    lane_dataset = LaneDataset(train_dir, img_size=640)

    print(f"Total training samples: {len(lane_dataset)}")

    # Load 3 samples and print statistics
    print("\nSample statistics (first 3 images):")
    for i in range(3):
        image_tensor, lanes, img_name = lane_dataset[i]
        num_lanes = len(lanes)

        print(f"\n  Sample {i+1}: {img_name}")
        print(f"    Image shape: {image_tensor.shape}")
        print(f"    Total lane markings (parallel + dashed): {num_lanes}")
        if num_lanes > 0:
            print(f"    Points per lane: {[len(lane) for lane in lanes]}")

    # Visualize one sample from each dataset
    print("\n" + "=" * 70)
    print("[3/3] Visualizing samples...")
    print("Displaying vehicle detection sample...")
    visualize_sample(vehicle_dataset, 0, dataset_type='vehicle')

    print("Displaying lane detection sample...")
    visualize_sample(lane_dataset, 0, dataset_type='lane')

    print("\n" + "=" * 70)
    print("Dataset loader testing complete!")
    print("=" * 70)
