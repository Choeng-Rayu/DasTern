"""
Pipeline orchestrator for the OCR Service.
Coordinates all 7 layers in sequence with timing and error handling.
"""

import time
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

from app.core.logging import get_logger, set_request_id
from app.core.exceptions import OCRServiceError
from app.intake.validator import ImageValidator
from app.quality.analyzer import QualityAnalyzer
from app.preprocess.enhancer import ImageEnhancer
from app.layout.detector import LayoutDetector
from app.ocr.extractor import OCRExtractor
from app.postprocess.cleaner import TextCleaner
from app.builder.json_builder import JSONBuilder
from app.schemas.responses import OCRResponse, QualityMetrics, ProcessingMeta

logger = get_logger(__name__)


@dataclass
class PipelineContext:
    """Context object passed through all pipeline stages."""
    
    # Input
    image_bytes: bytes
    filename: str
    
    # Request tracking
    request_id: str = ""
    
    # Stage outputs
    pil_image: Optional[Image.Image] = None
    cv_image: Optional[np.ndarray] = None
    quality_metrics: Optional[Dict[str, Any]] = None
    preprocessed_image: Optional[np.ndarray] = None
    layout_blocks: list = field(default_factory=list)
    ocr_results: list = field(default_factory=list)
    cleaned_results: list = field(default_factory=list)
    
    # Timing
    stage_times: Dict[str, float] = field(default_factory=dict)
    total_time_ms: float = 0.0
    
    # Errors
    errors: list = field(default_factory=list)


class OCRPipeline:
    """
    Main pipeline that orchestrates all 7 OCR layers.
    
    Layer 1: Image Intake & Validation
    Layer 2: Quality Analysis
    Layer 3: Preprocessing & Enhancement
    Layer 4: Layout Analysis
    Layer 5: OCR Extraction
    Layer 6: Post-processing
    Layer 7: JSON Builder
    """
    
    def __init__(self):
        """Initialize all layer components."""
        self.validator = ImageValidator()
        self.quality_analyzer = QualityAnalyzer()
        self.enhancer = ImageEnhancer()
        self.layout_detector = LayoutDetector()
        self.ocr_extractor = OCRExtractor()
        self.text_cleaner = TextCleaner()
        self.json_builder = JSONBuilder()
    
    async def process(
        self,
        image_bytes: bytes,
        filename: str,
        languages: Optional[str] = None,
        skip_enhancement: bool = False
    ) -> OCRResponse:
        """
        Process an image through all OCR layers.
        
        Args:
            image_bytes: Raw image bytes
            filename: Original filename
            languages: Override languages (e.g., "eng+khm")
            skip_enhancement: Skip preprocessing if image is already clean
        
        Returns:
            OCRResponse with structured OCR results
        """
        start_time = time.time()
        request_id = set_request_id()
        
        context = PipelineContext(
            image_bytes=image_bytes,
            filename=filename,
            request_id=request_id
        )
        
        logger.info(f"Starting OCR pipeline for {filename}")
        
        try:
            # Layer 1: Image Intake & Validation
            context = await self._run_layer(
                "validation",
                lambda: self.validator.validate(context),
                context
            )
            
            # Layer 2: Quality Analysis
            context = await self._run_layer(
                "quality_analysis",
                lambda: self.quality_analyzer.analyze(context),
                context
            )
            
            # Layer 3: Preprocessing & Enhancement
            if not skip_enhancement:
                context = await self._run_layer(
                    "preprocessing",
                    lambda: self.enhancer.enhance(context),
                    context
                )
            else:
                context.preprocessed_image = context.cv_image
                context.stage_times["preprocessing"] = 0.0
            
            # Layer 4: Layout Analysis
            context = await self._run_layer(
                "layout_analysis",
                lambda: self.layout_detector.detect(context),
                context
            )
            
            # Layer 5: OCR Extraction
            context = await self._run_layer(
                "ocr_extraction",
                lambda: self.ocr_extractor.extract(context, languages),
                context
            )
            
            # Layer 6: Post-processing
            context = await self._run_layer(
                "postprocessing",
                lambda: self.text_cleaner.clean(context),
                context
            )
            
            # Layer 7: JSON Builder
            context.total_time_ms = (time.time() - start_time) * 1000
            response = self.json_builder.build(context)
            
            logger.info(
                f"Pipeline completed in {context.total_time_ms:.0f}ms - "
                f"Blocks: {len(response.blocks)}"
            )
            
            return response
            
        except OCRServiceError:
            raise
        except Exception as e:
            logger.exception(f"Pipeline error: {e}")
            raise OCRServiceError(
                message=f"Pipeline processing failed: {str(e)}",
                details={"stage_times": context.stage_times}
            )
    
    async def _run_layer(
        self,
        layer_name: str,
        layer_func,
        context: PipelineContext
    ) -> PipelineContext:
        """Run a single layer with timing and error handling."""
        start = time.time()
        logger.debug(f"Starting layer: {layer_name}")
        
        try:
            result = layer_func()
            elapsed = (time.time() - start) * 1000
            context.stage_times[layer_name] = elapsed
            logger.debug(f"Layer {layer_name} completed in {elapsed:.0f}ms")
            return result
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            context.stage_times[layer_name] = elapsed
            logger.error(f"Layer {layer_name} failed after {elapsed:.0f}ms: {e}")
            raise
    
    async def analyze_quality_only(
        self,
        image_bytes: bytes,
        filename: str
    ) -> QualityMetrics:
        """
        Run only quality analysis without full OCR.
        Useful for previewing image quality before processing.
        """
        context = PipelineContext(
            image_bytes=image_bytes,
            filename=filename,
            request_id=set_request_id()
        )
        
        # Layer 1: Validation
        context = self.validator.validate(context)
        
        # Layer 2: Quality Analysis
        context = self.quality_analyzer.analyze(context)
        
        return QualityMetrics(**context.quality_metrics)
