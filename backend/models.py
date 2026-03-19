"""
Pydantic models for API request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class SpeedResult(BaseModel):
    """Individual speed measurement for a tracked vehicle."""
    track_id: int = Field(..., description="Unique tracking ID for the vehicle")
    speed_kmh: float = Field(..., description="Estimated average speed in km/h")
    max_speed_kmh: Optional[float] = Field(None, description="Maximum estimated speed in km/h")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    vehicle_type: Optional[str] = Field(None, description="Type of vehicle (car/truck/bus)")
    image_filename: Optional[str] = Field(None, description="Filename of vehicle crop image in vehicle_crops/")



class AnalysisResponse(BaseModel):
    """Response model for video analysis endpoints."""
    status: str = Field(..., description="Status of the analysis (success/error)")
    processing_time: float = Field(..., description="Processing time in seconds")
    total_frames: int = Field(..., description="Total number of frames processed")
    results: List[SpeedResult] = Field(default=[], description="List of speed measurements")
    error: Optional[str] = Field(None, description="Error message if analysis failed")
    metadata: Optional[dict] = Field(None, description="Additional metadata about the analysis")


class SampleRequest(BaseModel):
    """Request model for sample video analysis."""
    sample_name: Optional[str] = Field(
        "VID_20260311_085632",
        # "VID_20260319_182328",
        description="Name of the sample video to process (without extension)"
    )


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="API status")
    message: str = Field(..., description="Status message")
    models_loaded: bool = Field(..., description="Whether ML models are loaded")
    vehicle_model_path: Optional[str] = Field(None, description="Path to vehicle detection model")
    lane_model_path: Optional[str] = Field(None, description="Path to lane detection model")
