"""
Lane Detection Module - U-Net with ResNet-18 Backbone

Extracted from 03_lane_detection_clrnet.ipynb and 04_speed_estimation.ipynb
"""

import logging
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms

logger = logging.getLogger(__name__)


class SimpleLaneDetector(nn.Module):
    """
    U-Net style lane detection model with ResNet-18 backbone.

    Architecture from 03_lane_detection_clrnet.ipynb
    """

    def __init__(self, num_classes: int = 1):
        """
        Initialize lane detection model.

        Args:
            num_classes: Number of output classes (1 for binary segmentation)
        """
        super(SimpleLaneDetector, self).__init__()

        # Use ResNet18 as backbone
        resnet = models.resnet18(pretrained=False)

        # Encoder (ResNet backbone)
        self.layer0 = nn.Sequential(
            resnet.conv1, resnet.bn1, resnet.relu, resnet.maxpool
        )
        self.layer1 = resnet.layer1
        self.layer2 = resnet.layer2
        self.layer3 = resnet.layer3
        self.layer4 = resnet.layer4

        # Decoder (upsampling)
        self.up1 = nn.ConvTranspose2d(512, 256, kernel_size=2, stride=2)
        self.dec1 = self._make_decoder_block(512, 256)

        self.up2 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        self.dec2 = self._make_decoder_block(256, 128)

        self.up3 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.dec3 = self._make_decoder_block(128, 64)

        self.up4 = nn.ConvTranspose2d(64, 32, kernel_size=2, stride=2)
        self.dec4 = self._make_decoder_block(64, 32)

        # Final convolution
        self.final = nn.Sequential(
            nn.Conv2d(32, num_classes, kernel_size=1), nn.Sigmoid()
        )

    def _make_decoder_block(self, in_channels: int, out_channels: int) -> nn.Module:
        """Create a decoder block with two convolutions."""
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: Input tensor (B, C, H, W)

        Returns:
            Output segmentation mask (B, num_classes, H, W)
        """
        # Encoder
        x0 = self.layer0(x)
        x1 = self.layer1(x0)
        x2 = self.layer2(x1)
        x3 = self.layer3(x2)
        x4 = self.layer4(x3)

        # Decoder with skip connections
        up1 = self.up1(x4)
        cat1 = torch.cat([up1, x3], dim=1)
        dec1 = self.dec1(cat1)

        up2 = self.up2(dec1)
        cat2 = torch.cat([up2, x2], dim=1)
        dec2 = self.dec2(cat2)

        up3 = self.up3(dec2)
        cat3 = torch.cat([up3, x1], dim=1)
        dec3 = self.dec3(cat3)

        up4 = self.up4(dec3)
        cat4 = torch.cat([up4, x0], dim=1)
        dec4 = self.dec4(cat4)

        # Final output
        out = self.final(dec4)

        # Upsample to original size
        out = nn.functional.interpolate(
            out, scale_factor=4, mode="bilinear", align_corners=False
        )

        return out


class LaneDetector:
    """
    Lane detector wrapper for SimpleLaneDetector model.

    Provides high-level interface for lane detection from images.
    """

    def __init__(
        self,
        model_path: Optional[Path] = None,
        device: Optional[torch.device] = None,
        input_size: tuple = (640, 640),
    ):
        """
        Initialize lane detector.

        Args:
            model_path: Path to trained model weights
            device: Torch device (cuda/cpu)
            input_size: Input image size (height, width)
        """
        self.device = device or torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.input_size = input_size

        self.model = self._load_model(model_path)

        # Image preprocessing transform
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize(input_size),
            transforms.ToTensor(),
        ])

    def _load_model(self, model_path: Optional[Path]) -> Optional[SimpleLaneDetector]:
        """Load lane detection model."""
        try:
            if model_path and Path(model_path).exists():
                model = SimpleLaneDetector(num_classes=1).to(self.device)
                model.load_state_dict(
                    torch.load(model_path, map_location=self.device)
                )
                model.eval()
                logger.info(f"Loaded lane detector from: {model_path}")
                return model
            else:
                if model_path:
                    logger.warning(f"Lane model not found at {model_path}")
                logger.warning("Lane detection will not be available")
                return None

        except Exception as e:
            logger.error(f"Error loading lane detector: {e}")
            return None

    def detect(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Detect lanes in a frame.

        Args:
            frame: Input image (numpy array, RGB format)

        Returns:
            Lane segmentation mask (H, W) with values 0-1, or None if detection fails
        """
        if self.model is None:
            return None

        try:
            # Preprocess image
            image_tensor = self.transform(frame).unsqueeze(0).to(self.device)

            # Inference
            with torch.no_grad():
                lane_mask = self.model(image_tensor)
                lane_mask = lane_mask.squeeze().cpu().numpy()

            return lane_mask

        except Exception as e:
            logger.error(f"Error detecting lanes: {e}")
            return None

    def extract_polylines(
        self,
        mask: np.ndarray,
        threshold: float = 0.5,
        min_points: int = 10
    ) -> list:
        """
        Extract lane polylines from segmentation mask.

        Args:
            mask: Binary segmentation mask (H, W)
            threshold: Threshold for binarization
            min_points: Minimum number of points for a valid lane

        Returns:
            List of lane polylines, each as numpy array of (x, y) points
        """
        # Binarize mask
        binary_mask = (mask > threshold).astype(np.uint8) * 255

        # Find contours
        contours, _ = cv2.findContours(
            binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        lanes = []
        for contour in contours:
            # Approximate contour
            epsilon = 0.01 * cv2.arcLength(contour, False)
            approx = cv2.approxPolyDP(contour, epsilon, False)

            # Convert to polyline
            points = approx.squeeze()

            if len(points.shape) == 2 and len(points) >= min_points:
                # Sort by y-coordinate
                points = points[np.argsort(points[:, 1])]
                lanes.append(points)

        return lanes

    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model is not None
