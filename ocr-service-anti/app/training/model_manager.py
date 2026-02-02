"""
Model Manager

Manages trained Tesseract models:
- Version control
- A/B testing
- Activation/rollback
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import ModelNotFoundError

logger = get_logger(__name__)


@dataclass
class ModelMetadata:
    """Metadata for a trained model."""
    name: str
    version: str
    created_at: str
    base_language: str
    training_samples: int
    accuracy: Optional[float] = None
    description: Optional[str] = None
    is_active: bool = False


class ModelManager:
    """
    Manages trained Tesseract models.
    
    Features:
    - Model versioning
    - Activation/deactivation
    - Rollback to previous versions
    - A/B testing support
    """
    
    def __init__(self, models_dir: Optional[Path] = None):
        self.models_dir = models_dir or settings.custom_model_path
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.models_dir / "models_metadata.json"
        
        # Load existing metadata
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, ModelMetadata]:
        """Load metadata from disk."""
        if not self.metadata_file.exists():
            return {}
        
        try:
            with open(self.metadata_file) as f:
                data = json.load(f)
            return {
                name: ModelMetadata(**info) 
                for name, info in data.items()
            }
        except Exception as e:
            logger.warning(f"Could not load metadata: {e}")
            return {}
    
    def _save_metadata(self) -> None:
        """Save metadata to disk."""
        data = {
            name: asdict(meta) 
            for name, meta in self.metadata.items()
        }
        with open(self.metadata_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def register_model(
        self,
        name: str,
        traineddata_path: Path,
        base_language: str = "khm",
        training_samples: int = 0,
        description: Optional[str] = None
    ) -> ModelMetadata:
        """
        Register a new trained model.
        """
        # Create version (timestamp-based)
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create model directory
        model_dir = self.models_dir / name
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy traineddata file
        dest_path = model_dir / f"{name}.traineddata"
        shutil.copy(traineddata_path, dest_path)
        
        # Create metadata
        meta = ModelMetadata(
            name=name,
            version=version,
            created_at=datetime.now().isoformat(),
            base_language=base_language,
            training_samples=training_samples,
            description=description,
            is_active=False
        )
        
        self.metadata[name] = meta
        self._save_metadata()
        
        logger.info(f"Registered model: {name} (v{version})")
        return meta
    
    def get_model(self, name: str) -> Optional[ModelMetadata]:
        """Get model metadata by name."""
        return self.metadata.get(name)
    
    def list_models(self) -> List[ModelMetadata]:
        """List all registered models."""
        return list(self.metadata.values())
    
    def activate_model(self, name: str) -> None:
        """
        Activate a model for use.
        
        This sets the model as the default for OCR processing.
        """
        if name not in self.metadata and name != "default":
            raise ModelNotFoundError(
                message=f"Model not found: {name}"
            )
        
        # Deactivate all other models
        for meta in self.metadata.values():
            meta.is_active = False
        
        # Activate requested model
        if name in self.metadata:
            self.metadata[name].is_active = True
        
        # Update settings
        settings.active_model = name
        
        self._save_metadata()
        logger.info(f"Activated model: {name}")
    
    def get_active_model(self) -> str:
        """Get the currently active model name."""
        for name, meta in self.metadata.items():
            if meta.is_active:
                return name
        return "default"
    
    def delete_model(self, name: str) -> None:
        """
        Delete a model and its files.
        """
        if name not in self.metadata:
            raise ModelNotFoundError(message=f"Model not found: {name}")
        
        # Check if active
        if self.metadata[name].is_active:
            # Switch to default first
            self.activate_model("default")
        
        # Remove files
        model_dir = self.models_dir / name
        if model_dir.exists():
            shutil.rmtree(model_dir)
        
        # Remove from metadata
        del self.metadata[name]
        self._save_metadata()
        
        logger.info(f"Deleted model: {name}")
    
    def get_model_path(self, name: str) -> Optional[Path]:
        """Get path to model's traineddata file."""
        if name == "default":
            return None  # Use system tessdata
        
        model_path = self.models_dir / name / f"{name}.traineddata"
        if model_path.exists():
            return model_path
        
        return None
    
    def compare_models(
        self,
        model_a: str,
        model_b: str,
        test_images: List[Path]
    ) -> Dict[str, Any]:
        """
        Compare two models on test images.
        
        Useful for A/B testing before switching models.
        """
        # TODO: Implement comparison
        # 1. Run both models on test images
        # 2. Compare accuracy metrics
        # 3. Return comparison results
        
        return {
            "model_a": model_a,
            "model_b": model_b,
            "test_images": len(test_images),
            "comparison": "Not yet implemented"
        }
    
    def export_model(self, name: str, output_path: Path) -> Path:
        """
        Export a model for use elsewhere.
        """
        if name not in self.metadata:
            raise ModelNotFoundError(message=f"Model not found: {name}")
        
        model_path = self.get_model_path(name)
        if not model_path:
            raise ModelNotFoundError(message=f"Model files not found: {name}")
        
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        
        dest = output_path / f"{name}.traineddata"
        shutil.copy(model_path, dest)
        
        # Also export metadata
        meta_dest = output_path / f"{name}_metadata.json"
        with open(meta_dest, 'w') as f:
            json.dump(asdict(self.metadata[name]), f, indent=2)
        
        logger.info(f"Exported model {name} to {output_path}")
        return dest
