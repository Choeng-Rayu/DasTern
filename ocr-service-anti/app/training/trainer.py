"""
Tesseract Training Module

Orchestrates the training pipeline for custom Tesseract models.
Fine-tunes LSTM models for specific prescription fonts.
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import TrainingError

logger = get_logger(__name__)


@dataclass
class TrainingConfig:
    """Configuration for training a model."""
    model_name: str
    base_language: str = "khm"
    max_iterations: int = 400
    learning_rate: float = 0.001
    target_error_rate: float = 0.01
    debug_interval: int = 100


class TesseractTrainer:
    """
    Trains custom Tesseract LSTM models.
    
    Training flow:
    1. Extract LSTM from base model
    2. Prepare training data (images + box files)
    3. Run lstmtraining
    4. Combine into .traineddata
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or settings.custom_model_path
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Tesseract training tools
        self.combine_tessdata = shutil.which("combine_tessdata")
        self.lstmtraining = shutil.which("lstmtraining")
        self.tesseract = shutil.which("tesseract")
        
        # Verify tools are available
        self._verify_tools()
    
    def _verify_tools(self) -> None:
        """Verify required training tools are installed."""
        missing = []
        if not self.combine_tessdata:
            missing.append("combine_tessdata")
        if not self.lstmtraining:
            missing.append("lstmtraining")
        if not self.tesseract:
            missing.append("tesseract")
        
        if missing:
            logger.warning(
                f"Training tools not found: {missing}. "
                "Install tesseract-ocr-training for training support."
            )
    
    def train(
        self,
        config: TrainingConfig,
        training_files: List[Path],
        callback: Optional[callable] = None
    ) -> Path:
        """
        Train a new Tesseract model.
        
        Args:
            config: Training configuration
            training_files: List of .lstmf training files
            callback: Progress callback function
        
        Returns:
            Path to the trained model
        """
        logger.info(f"Starting training for model: {config.model_name}")
        
        if not self.lstmtraining:
            raise TrainingError(
                message="lstmtraining not found. Install tesseract-ocr-training."
            )
        
        # Create model directory
        model_dir = self.output_dir / config.model_name
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Create training list file
        train_list = model_dir / "training_files.txt"
        with open(train_list, 'w') as f:
            for tf in training_files:
                f.write(str(tf) + "\n")
        
        try:
            # Extract LSTM from base model
            checkpoint = self._extract_lstm(config.base_language, model_dir)
            
            # Run LSTM training
            output_checkpoint = self._run_training(
                config=config,
                checkpoint=checkpoint,
                train_list=train_list,
                model_dir=model_dir,
                callback=callback
            )
            
            # Combine into .traineddata
            traineddata = self._combine_model(
                config=config,
                checkpoint=output_checkpoint,
                model_dir=model_dir
            )
            
            logger.info(f"Training complete: {traineddata}")
            return traineddata
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise TrainingError(message=f"Training failed: {str(e)}")
    
    def _extract_lstm(self, base_language: str, output_dir: Path) -> Path:
        """Extract LSTM from base language model."""
        # Find tessdata directory
        tessdata_dir = self._find_tessdata()
        base_model = tessdata_dir / f"{base_language}.traineddata"
        
        if not base_model.exists():
            raise TrainingError(
                message=f"Base model not found: {base_language}",
                details={"tessdata_dir": str(tessdata_dir)}
            )
        
        # Extract LSTM component
        lstm_output = output_dir / f"{base_language}.lstm"
        
        cmd = [
            self.combine_tessdata,
            "-e",
            str(base_model),
            str(lstm_output)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise TrainingError(
                message=f"Failed to extract LSTM: {result.stderr}"
            )
        
        return lstm_output
    
    def _run_training(
        self,
        config: TrainingConfig,
        checkpoint: Path,
        train_list: Path,
        model_dir: Path,
        callback: Optional[callable] = None
    ) -> Path:
        """Run LSTM training."""
        output_checkpoint = model_dir / config.model_name
        
        cmd = [
            self.lstmtraining,
            "--model_output", str(output_checkpoint),
            "--traineddata", str(self._find_tessdata() / f"{config.base_language}.traineddata"),
            "--train_listfile", str(train_list),
            "--max_iterations", str(config.max_iterations),
            "--learning_rate", str(config.learning_rate),
            "--target_error_rate", str(config.target_error_rate),
            "--debug_interval", str(config.debug_interval),
        ]
        
        if checkpoint.exists():
            cmd.extend(["--continue_from", str(checkpoint)])
        
        logger.info(f"Running: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Monitor progress
        for line in process.stdout:
            logger.debug(line.strip())
            
            # Parse progress if callback provided
            if callback and "At iteration" in line:
                try:
                    iteration = int(line.split("At iteration")[1].split()[0])
                    progress = min(100, (iteration / config.max_iterations) * 100)
                    callback(progress, line.strip())
                except Exception:
                    pass
        
        process.wait()
        
        if process.returncode != 0:
            raise TrainingError(message="LSTM training failed")
        
        return output_checkpoint
    
    def _combine_model(
        self,
        config: TrainingConfig,
        checkpoint: Path,
        model_dir: Path
    ) -> Path:
        """Combine trained LSTM into .traineddata file."""
        traineddata = model_dir / f"{config.model_name}.traineddata"
        
        # Copy base model components
        tessdata_dir = self._find_tessdata()
        base_model = tessdata_dir / f"{config.base_language}.traineddata"
        
        # Extract all components from base
        extract_cmd = [
            self.combine_tessdata,
            "-u",
            str(base_model),
            str(model_dir / config.base_language)
        ]
        subprocess.run(extract_cmd, capture_output=True)
        
        # Replace LSTM with trained one
        trained_lstm = Path(f"{checkpoint}_checkpoint")
        if trained_lstm.exists():
            shutil.copy(trained_lstm, model_dir / f"{config.model_name}.lstm")
        
        # Combine components
        combine_cmd = [
            self.combine_tessdata,
            str(model_dir / config.model_name)
        ]
        result = subprocess.run(combine_cmd, capture_output=True, text=True)
        
        if not traineddata.exists():
            raise TrainingError(message=f"Failed to create traineddata: {result.stderr}")
        
        return traineddata
    
    def _find_tessdata(self) -> Path:
        """Find Tesseract data directory."""
        # Common locations
        paths = [
            Path("/usr/share/tesseract-ocr/4.00/tessdata"),
            Path("/usr/share/tesseract-ocr/5/tessdata"),
            Path("/usr/share/tessdata"),
            Path("/usr/local/share/tessdata"),
        ]
        
        # Check TESSDATA_PREFIX env
        if "TESSDATA_PREFIX" in os.environ:
            paths.insert(0, Path(os.environ["TESSDATA_PREFIX"]))
        
        for path in paths:
            if path.exists() and (path / "eng.traineddata").exists():
                return path
        
        raise TrainingError(
            message="Could not find tessdata directory",
            details={"checked": [str(p) for p in paths]}
        )
    
    def evaluate(
        self,
        model_path: Path,
        test_images: List[Path]
    ) -> Dict[str, Any]:
        """
        Evaluate model accuracy on test images.
        
        Returns:
            Dictionary with accuracy metrics
        """
        # TODO: Implement evaluation
        # 1. Run OCR with model
        # 2. Compare with ground truth
        # 3. Calculate CER/WER
        
        return {
            "model": str(model_path),
            "test_images": len(test_images),
            "accuracy": None,
            "message": "Evaluation not yet implemented"
        }
