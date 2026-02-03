"""
Training Data Generator

Generates synthetic training data and prepares real images
for Tesseract LSTM training.
"""

import io
import random
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


@dataclass
class TrainingImage:
    """Represents a training image with ground truth."""
    image: np.ndarray
    text: str
    box_data: str  # Tesseract box format
    filename: str


class TrainingDataGenerator:
    """
    Generates training data for Tesseract fine-tuning.
    
    Can create:
    - Synthetic images with known text
    - Augmented versions of real images
    - Box files for OCR training
    """
    
    def __init__(self, fonts_dir: Optional[Path] = None):
        self.fonts_dir = fonts_dir or Path("./training_data/fonts")
        self.fonts_dir.mkdir(parents=True, exist_ok=True)
        
        # Default fonts to try
        self.default_fonts = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/usr/share/fonts/khmer/KhmerOS.ttf",
        ]
    
    def generate_synthetic(
        self,
        text_samples: List[str],
        output_dir: Path,
        variations: int = 5
    ) -> List[TrainingImage]:
        """
        Generate synthetic training images from text samples.
        
        Args:
            text_samples: List of text strings to render
            output_dir: Directory to save generated images
            variations: Number of variations per sample
        
        Returns:
            List of TrainingImage objects
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        training_images = []
        
        for text in text_samples:
            for i in range(variations):
                # Generate image with variations
                img, box_data = self._render_text_image(
                    text=text,
                    variation_seed=i
                )
                
                filename = f"synthetic_{hash(text) % 10000}_{i}"
                
                training_images.append(TrainingImage(
                    image=img,
                    text=text,
                    box_data=box_data,
                    filename=filename
                ))
        
        logger.info(f"Generated {len(training_images)} synthetic images")
        return training_images
    
    def _render_text_image(
        self,
        text: str,
        variation_seed: int = 0
    ) -> Tuple[np.ndarray, str]:
        """
        Render text as an image with variations.
        """
        random.seed(variation_seed)
        
        # Image settings
        padding = 20
        font_size = random.randint(24, 48)
        
        # Load font
        font = self._load_font(font_size)
        
        # Calculate image size
        dummy_img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(dummy_img)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Create image
        width = text_width + padding * 2
        height = text_height + padding * 2
        
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw text
        text_x = padding
        text_y = padding
        draw.text((text_x, text_y), text, font=font, fill='black')
        
        # Apply variations
        img_array = np.array(img)
        img_array = self._apply_augmentation(img_array, variation_seed)
        
        # Generate box data
        box_data = self._generate_box_data(
            text=text,
            x=text_x,
            y=text_y,
            width=text_width,
            height=text_height,
            image_height=height
        )
        
        return img_array, box_data
    
    def _load_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Load a font for rendering."""
        # Try custom fonts first
        if self.fonts_dir.exists():
            for font_file in self.fonts_dir.glob("*.ttf"):
                try:
                    return ImageFont.truetype(str(font_file), size)
                except Exception:
                    continue
        
        # Try default system fonts
        for font_path in self.default_fonts:
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue
        
        # Fallback to default font
        return ImageFont.load_default()
    
    def _apply_augmentation(
        self,
        image: np.ndarray,
        seed: int
    ) -> np.ndarray:
        """Apply random augmentations to image."""
        random.seed(seed)
        
        # Random blur
        if random.random() > 0.5:
            kernel_size = random.choice([3, 5])
            image = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        
        # Random noise
        if random.random() > 0.5:
            noise = np.random.normal(0, random.randint(5, 15), image.shape)
            image = np.clip(image + noise, 0, 255).astype(np.uint8)
        
        # Random rotation (small angle)
        if random.random() > 0.5:
            angle = random.uniform(-2, 2)
            h, w = image.shape[:2]
            M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1)
            image = cv2.warpAffine(image, M, (w, h), borderValue=(255, 255, 255))
        
        # Random contrast/brightness
        if random.random() > 0.5:
            alpha = random.uniform(0.8, 1.2)  # Contrast
            beta = random.randint(-20, 20)     # Brightness
            image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        
        return image
    
    def _generate_box_data(
        self,
        text: str,
        x: int,
        y: int,
        width: int,
        height: int,
        image_height: int
    ) -> str:
        """
        Generate Tesseract box file data.
        
        Box format: char x1 y1 x2 y2 page
        Note: y coordinates are from bottom of image
        """
        lines = []
        
        # For simplicity, treat each character as evenly spaced
        char_width = width / max(len(text), 1)
        
        for i, char in enumerate(text):
            if char == ' ':
                continue
            
            char_x1 = int(x + i * char_width)
            char_x2 = int(x + (i + 1) * char_width)
            
            # Tesseract uses bottom-left origin
            char_y1 = image_height - y - height
            char_y2 = image_height - y
            
            lines.append(f"{char} {char_x1} {char_y1} {char_x2} {char_y2} 0")
        
        return "\n".join(lines)
    
    def create_lstmf_from_image(
        self,
        image_path: Path,
        box_path: Path,
        output_path: Path,
        language: str = "khm"
    ) -> Path:
        """
        Create .lstmf training file from image and box file.
        
        Uses tesseract to generate the training data.
        """
        import subprocess
        
        # Run tesseract to create lstmf
        cmd = [
            "tesseract",
            str(image_path),
            str(output_path.with_suffix('')),
            "-l", language,
            "--psm", "6",
            "lstm.train"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        lstmf_path = output_path.with_suffix('.lstmf')
        if lstmf_path.exists():
            return lstmf_path
        
        logger.error(f"Failed to create lstmf: {result.stderr}")
        return None
    
    def save_training_data(
        self,
        training_images: List[TrainingImage],
        output_dir: Path
    ) -> Dict[str, Path]:
        """
        Save training images and box files to disk.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        saved = {"images": [], "boxes": []}
        
        for ti in training_images:
            # Save image
            img_path = output_dir / f"{ti.filename}.png"
            cv2.imwrite(str(img_path), ti.image)
            saved["images"].append(img_path)
            
            # Save box file
            box_path = output_dir / f"{ti.filename}.box"
            with open(box_path, 'w', encoding='utf-8') as f:
                f.write(ti.box_data)
            saved["boxes"].append(box_path)
        
        logger.info(f"Saved {len(training_images)} training pairs to {output_dir}")
        return saved


# Common Cambodian prescription terms for training
PRESCRIPTION_TERMS = {
    "khmer": [
        "ព្រឹក", "ល្ងាច", "យប់", "ថ្ងៃ",
        "គ្រាប់", "ស្លាបព្រា", 
        "មុនបាយ", "ក្រោយបាយ",
        "ម្តង", "២ម្តង", "៣ម្តង",
        "ថ្នាំ", "រោគ", "ជំងឺ",
    ],
    "english": [
        "Paracetamol", "Amoxicillin", "Omeprazole",
        "tablet", "capsule", "mg", "ml",
        "once", "twice", "three times",
        "morning", "evening", "night",
        "before meal", "after meal",
    ],
    "french": [
        "comprimé", "gélule", "sirop",
        "matin", "soir", "nuit",
        "avant repas", "après repas",
    ]
}
