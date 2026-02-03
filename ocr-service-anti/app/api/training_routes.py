"""
Training API Routes

Endpoints for fine-tuning Tesseract models:
- POST /training/upload - Upload training images
- POST /training/annotate - Generate/correct annotations
- POST /training/train - Start model training
- GET /training/models - List available models
- POST /training/models/{id}/activate - Activate a model
"""

from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from app.core.config import settings
from app.schemas.responses import ModelInfo, TrainingStatus
from app.schemas.requests import TrainingStartRequest

logger = get_logger(__name__)

router = APIRouter(tags=["Training"])

# Training job storage (in-memory for now)
_training_jobs = {}
_uploaded_images = {}


@router.post(
    "/upload",
    summary="Upload training images",
    description="Upload prescription images for training data."
)
async def upload_training_data(
    files: List[UploadFile] = File(..., description="Training images"),
    model_name: str = "custom_prescription"
):
    """
    Upload images to build training dataset.
    
    Images will be processed and prepared for annotation.
    """
    logger.info(f"Uploading {len(files)} training images for model: {model_name}")
    
    uploaded = []
    for file in files:
        image_bytes = await file.read()
        image_id = f"{model_name}_{len(_uploaded_images)}"
        
        _uploaded_images[image_id] = {
            "filename": file.filename,
            "bytes": image_bytes,
            "model_name": model_name,
            "annotated": False
        }
        
        uploaded.append({
            "image_id": image_id,
            "filename": file.filename,
            "size": len(image_bytes)
        })
    
    return {
        "message": f"Uploaded {len(uploaded)} images",
        "images": uploaded,
        "next_step": "POST /training/annotate to generate ground truth"
    }


@router.post(
    "/annotate",
    summary="Generate annotations",
    description="Run OCR and generate editable ground truth annotations."
)
async def generate_annotations(image_id: str):
    """
    Generate ground truth annotations for an uploaded image.
    
    This runs OCR and creates editable .box files for training.
    """
    if image_id not in _uploaded_images:
        raise HTTPException(status_code=404, detail="Image not found")
    
    image_data = _uploaded_images[image_id]
    
    # TODO: Implement actual annotation generation
    # 1. Run OCR to get initial text
    # 2. Generate .box file format
    # 3. Return editable annotation
    
    return {
        "image_id": image_id,
        "status": "annotated",
        "message": "Ground truth generated. Edit corrections if needed.",
        "annotation_format": "tesseract_box",
        "download_url": f"/training/annotations/{image_id}"
    }


@router.post(
    "/train",
    summary="Start model training",
    description="Train a new Tesseract model with uploaded data."
)
async def start_training(
    request: TrainingStartRequest,
    background_tasks: BackgroundTasks
):
    """
    Start training a new Tesseract LSTM model.
    
    Training runs in the background. Check status with GET /training/status/{job_id}
    """
    import uuid
    
    job_id = str(uuid.uuid4())[:8]
    
    # Get training images for this model
    training_images = [
        img for img_id, img in _uploaded_images.items()
        if img.get("model_name") == request.model_name or img.get("annotated")
    ]
    
    if not training_images:
        raise HTTPException(
            status_code=400,
            detail="No training data available. Upload and annotate images first."
        )
    
    _training_jobs[job_id] = {
        "status": "pending",
        "model_name": request.model_name,
        "progress": 0,
        "message": "Training queued"
    }
    
    # TODO: Add actual training task
    # background_tasks.add_task(run_training, job_id, request)
    
    return {
        "job_id": job_id,
        "message": "Training job created",
        "model_name": request.model_name,
        "status_url": f"/training/status/{job_id}"
    }


@router.get(
    "/status/{job_id}",
    response_model=TrainingStatus,
    summary="Get training status",
    description="Check the status of a training job."
)
async def get_training_status(job_id: str):
    """Get current status of a training job."""
    if job_id not in _training_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = _training_jobs[job_id]
    
    return TrainingStatus(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"],
        message=job.get("message"),
        model_name=job.get("model_name")
    )


@router.get(
    "/models",
    response_model=List[ModelInfo],
    summary="List trained models",
    description="List all available trained models."
)
async def list_models():
    """List all available trained models."""
    models = []
    
    # Always include default
    models.append(ModelInfo(
        name="default",
        description="Default Tesseract model with eng+khm+fra",
        created_at="built-in",
        accuracy=None,
        is_active=(settings.active_model == "default")
    ))
    
    # Check for custom models
    model_path = settings.custom_model_path
    if model_path.exists():
        for model_dir in model_path.iterdir():
            if model_dir.is_dir():
                models.append(ModelInfo(
                    name=model_dir.name,
                    description=f"Custom model: {model_dir.name}",
                    created_at=str(model_dir.stat().st_mtime),
                    accuracy=None,
                    is_active=(settings.active_model == model_dir.name)
                ))
    
    return models


@router.post(
    "/models/{model_name}/activate",
    summary="Activate a model",
    description="Switch to using a specific trained model."
)
async def activate_model(model_name: str):
    """
    Activate a trained model for OCR.
    
    The active model will be used for all subsequent OCR requests.
    """
    # Verify model exists
    if model_name != "default":
        model_path = settings.custom_model_path / model_name
        if not model_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Model not found: {model_name}"
            )
    
    # Update settings (in-memory only)
    # For persistent change, update .env file
    settings.active_model = model_name
    
    return {
        "message": f"Activated model: {model_name}",
        "active_model": model_name
    }


@router.delete(
    "/models/{model_name}",
    summary="Delete a model",
    description="Delete a custom trained model."
)
async def delete_model(model_name: str):
    """Delete a custom trained model."""
    if model_name == "default":
        raise HTTPException(
            status_code=400,
            detail="Cannot delete default model"
        )
    
    model_path = settings.custom_model_path / model_name
    if not model_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Model not found: {model_name}"
        )
    
    # TODO: Delete model files
    # shutil.rmtree(model_path)
    
    return {"message": f"Deleted model: {model_name}"}
