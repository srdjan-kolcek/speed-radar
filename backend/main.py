"""
FastAPI Backend for Speed Radar - Vehicle Speed Estimation API

This backend provides REST API endpoints for analyzing video footage
and estimating vehicle speeds using ML models.
"""

import logging
import time
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import (
    ALLOWED_ORIGINS,
    API_DESCRIPTION,
    API_TITLE,
    API_VERSION,
    LANE_MODEL_PATH,
    MAX_VIDEO_SIZE_MB,
    VEHICLE_MODEL_PATH,
    OUTPUT_DIR,
)
from .models import AnalysisResponse, HealthResponse, SampleRequest, SpeedResult
from .video_processor import VideoProcessor

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Set ml_pipeline to DEBUG
logging.getLogger("ml_pipeline").setLevel(logging.DEBUG)

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount vehicle crops directory as static files
crops_dir = OUTPUT_DIR / "vehicle_crops"
crops_dir.mkdir(parents=True, exist_ok=True)
app.mount("/vehicle_crops", StaticFiles(directory=str(crops_dir)), name="vehicle_crops")

# Global video processor instance
video_processor: Optional[VideoProcessor] = None

# Sample video name
SAMPLE_VIDEO_NAME = "VID_20260311_085632"
# SAMPLE_VIDEO_NAME = "VID_20260319_182328"


@app.on_event("startup")
async def startup_event():
    """Initialize ML models on startup."""
    global video_processor

    logger.info("Starting Speed Radar API...")
    logger.info(f"Version: {API_VERSION}")

    try:
        # Initialize video processor (loads ML models)
        video_processor = VideoProcessor()
        logger.info("ML models loaded successfully")
        logger.info("Speed Radar API is ready")

    except Exception as e:
        logger.error(f"Error loading ML models: {e}", exc_info=True)
        logger.warning("API started but ML models may not be available")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Speed Radar API...")


@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "status": "running",
        "endpoints": {
            "health": "/health",
            "analyze_upload": "/analyze/upload",
            "analyze_sample": "/analyze/sample",
            "docs": "/docs",
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health():
    """
    Health check endpoint.

    Returns API status and model loading information.
    """
    if video_processor is None:
        return HealthResponse(
            status="unhealthy",
            message="Video processor not initialized",
            models_loaded=False,
        )

    models_loaded = video_processor.is_ready()

    return HealthResponse(
        status="healthy" if models_loaded else "degraded",
        message="All systems operational" if models_loaded else "ML models not fully loaded",
        models_loaded=models_loaded,
        vehicle_model_path=str(VEHICLE_MODEL_PATH) if VEHICLE_MODEL_PATH.exists() else None,
        lane_model_path=str(LANE_MODEL_PATH) if LANE_MODEL_PATH.exists() else None,
    )


@app.post("/analyze/upload", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_upload(video: UploadFile = File(...)):
    """
    Upload and analyze a video file.

    Processes the uploaded video through the ML pipeline and returns
    speed estimations for detected vehicles.

    Args:
        video: Video file (MP4, AVI, MOV)

    Returns:
        AnalysisResponse with speed results
    """
    if video_processor is None:
        raise HTTPException(
            status_code=503,
            detail="Video processor not initialized"
        )

    start_time = time.time()

    try:
        logger.info(f"Received upload: {video.filename}")

        # Save uploaded file
        video_path = video_processor.save_upload(video, max_size_mb=MAX_VIDEO_SIZE_MB)

        try:
            # Process video
            logger.info(f"Processing video: {video_path}")
            process_results = video_processor.process_video(str(video_path))

            # Clean up uploaded file
            video_path.unlink(missing_ok=True)

            if not process_results["successful"]:
                raise HTTPException(
                    status_code=500,
                    detail=process_results.get("error", "Video processing failed")
                )

            processing_time = time.time() - start_time

            # Convert results to SpeedResult models
            speed_results = [
                SpeedResult(**result) for result in process_results["results"]
            ]

            logger.info(f"Processing complete: {len(speed_results)} vehicles detected")

            return AnalysisResponse(
                status="success",
                processing_time=processing_time,
                total_frames=process_results["total_frames"],
                results=speed_results,
                metadata={
                    "fps": process_results["fps"],
                    "filename": video.filename,
                }
            )

        finally:
            # Ensure cleanup
            if video_path.exists():
                video_path.unlink(missing_ok=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing upload: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/sample", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_sample():
    """
    Analyze the preloaded sample video.

    Processes the sample video stored on the server.

    Returns:
        AnalysisResponse with speed results
    """
    if video_processor is None:
        raise HTTPException(
            status_code=503,
            detail="Video processor not initialized"
        )

    start_time = time.time()

    try:
        # Use the hardcoded sample video
        video_path = f"{SAMPLE_VIDEO_NAME}.mp4"

        logger.info(f"Processing sample video: {video_path}")

        # Process video
        process_results = video_processor.process_video(video_path)

        if not process_results["successful"]:
            raise HTTPException(
                status_code=500,
                detail=process_results.get("error", "Video processing failed")
            )

        processing_time = time.time() - start_time

        # Convert results to SpeedResult models
        speed_results = [
            SpeedResult(**result) for result in process_results["results"]
        ]

        logger.info(f"Processing complete: {len(speed_results)} vehicles detected")

        return AnalysisResponse(
            status="success",
            processing_time=processing_time,
            total_frames=process_results["total_frames"],
            results=speed_results,
            metadata={
                "fps": process_results["fps"],
                "sample_name": SAMPLE_VIDEO_NAME,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing sample: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/samples/list", tags=["Analysis"])
async def list_samples():
    """
    List available sample videos.

    Returns:
        List with the single sample video name
    """
    try:
        return {"samples": [SAMPLE_VIDEO_NAME]}

    except Exception as e:
        logger.error(f"Error listing samples: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
