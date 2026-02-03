"""
Layer 6: OCR Post-processing

Purpose: Clean OCR noise WITHOUT interpretation
- Merge broken words (especially Khmer)
- Normalize whitespace
- Preserve original text and language
- DO NOT translate
- Character-level safe fixes only

Only safe fixes - no semantic understanding.
"""

import re
import unicodedata
from typing import List, Optional, Set

from app.core.logging import get_logger
from app.core.exceptions import PostProcessingError
from app.ocr.extractor import OCRBlock, OCRLine, OCRWord

logger = get_logger(__name__)


class TextCleaner:
    """
    Cleans and normalizes OCR output.
    
    Focuses on:
    - Khmer Unicode normalization
    - Fixing common OCR errors
    - Merging broken words
    - Whitespace normalization
    
    Does NOT:
    - Translate text
    - Interpret meaning
    - Remove "bad" text
    """
    
    def __init__(self):
        # Khmer Unicode range
        self.khmer_range = range(0x1780, 0x17FF + 1)
        
        # Common OCR substitution errors
        self.common_fixes = {
            # Latin
            '|': 'I',
            '0': 'O',  # Context-dependent
            '1': 'l',  # Context-dependent
            # Keep these conservative
        }
        
        # Khmer vowel clusters that often get split
        self.khmer_vowel_signs = set('ាិីឹឺុូួើឿៀេែៃោៅំះៈ៉៊់៌៍៎៏័៑្')
    
    def clean(self, context) -> 'PipelineContext':
        """
        Clean and normalize OCR results.
        
        Args:
            context: PipelineContext with ocr_results
        
        Returns:
            Updated context with cleaned_results
        """
        logger.info("Post-processing OCR results")
        
        try:
            cleaned_results = []
            
            for block in context.ocr_results:
                cleaned_block = self._clean_block(block)
                cleaned_results.append(cleaned_block)
            
            context.cleaned_results = cleaned_results
            
            logger.info(f"Cleaned {len(cleaned_results)} blocks")
            
            return context
            
        except Exception as e:
            logger.error(f"Post-processing failed: {e}")
            raise PostProcessingError(
                message=f"Post-processing failed: {str(e)}"
            )
    
    def _clean_block(self, block: OCRBlock) -> OCRBlock:
        """Clean a single OCR block."""
        cleaned_lines = []
        
        for line in block.lines:
            cleaned_line = self._clean_line(line)
            if cleaned_line.text.strip():  # Keep non-empty lines
                cleaned_lines.append(cleaned_line)
        
        block.lines = cleaned_lines
        return block
    
    def _clean_line(self, line: OCRLine) -> OCRLine:
        """Clean a single line of text."""
        # Clean individual words
        cleaned_words = []
        for word in line.words:
            cleaned_text = self._clean_text(word.text)
            if cleaned_text:
                word.text = cleaned_text
                cleaned_words.append(word)
        
        # Merge broken Khmer words
        merged_words = self._merge_broken_khmer(cleaned_words)
        
        # Update line
        line.words = merged_words
        line.text = " ".join(w.text for w in merged_words)
        
        # Recalculate confidence
        if merged_words:
            line.confidence = sum(w.confidence for w in merged_words) / len(merged_words)
        
        return line
    
    def _clean_text(self, text: str) -> str:
        """
        Clean a text string.
        """
        if not text:
            return ""
        
        # Normalize Unicode (NFC)
        text = unicodedata.normalize('NFC', text)
        
        # Normalize whitespace
        text = self._normalize_whitespace(text)
        
        # Normalize Khmer text
        if self._contains_khmer(text):
            text = self._normalize_khmer(text)
        
        return text.strip()
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace while preserving structure."""
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Remove zero-width characters that break words
        text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
        
        return text
    
    def _contains_khmer(self, text: str) -> bool:
        """Check if text contains Khmer characters."""
        return any(ord(c) in self.khmer_range for c in text)
    
    def _normalize_khmer(self, text: str) -> str:
        """
        Normalize Khmer text.
        Fixes common OCR issues with Khmer script.
        """
        # Fix broken subscript consonants
        # The ្  (coeng) should connect consonants
        text = re.sub(r'([ក-ឳ])\s+(្[ក-ឳ])', r'\1\2', text)
        
        # Fix separated vowel signs
        for vowel in self.khmer_vowel_signs:
            pattern = r'([ក-ឳ])\s+(' + re.escape(vowel) + ')'
            text = re.sub(pattern, r'\1\2', text)
        
        # Fix common OCR confusion (if we have training data for this)
        # Be very conservative - don't break valid text
        
        return text
    
    def _merge_broken_khmer(self, words: List[OCRWord]) -> List[OCRWord]:
        """
        Merge words that were incorrectly split.
        Especially important for Khmer where vowels may be separated.
        """
        if not words:
            return words
        
        merged = []
        i = 0
        
        while i < len(words):
            current = words[i]
            
            # Check if this is a standalone Khmer vowel that should merge
            if self._is_orphan_khmer_sign(current.text):
                if merged:
                    # Merge with previous word
                    prev = merged[-1]
                    prev.text = prev.text + current.text
                    prev.width = (current.x + current.width) - prev.x
                    prev.confidence = (prev.confidence + current.confidence) / 2
                    i += 1
                    continue
            
            # Check if next word should merge
            if i + 1 < len(words):
                next_word = words[i + 1]
                
                # Merge if next word starts with orphan sign and is close
                if self._should_merge(current, next_word):
                    current.text = current.text + next_word.text
                    current.width = (next_word.x + next_word.width) - current.x
                    current.confidence = (current.confidence + next_word.confidence) / 2
                    i += 2  # Skip next word
                    merged.append(current)
                    continue
            
            merged.append(current)
            i += 1
        
        return merged
    
    def _is_orphan_khmer_sign(self, text: str) -> bool:
        """Check if text is just a Khmer sign that got separated."""
        if len(text) > 2:
            return False
        return all(c in self.khmer_vowel_signs for c in text)
    
    def _should_merge(self, word1: OCRWord, word2: OCRWord) -> bool:
        """
        Determine if two words should be merged.
        """
        # Check if word2 starts with orphan sign
        if not self._is_orphan_khmer_sign(word2.text[:1] if word2.text else ''):
            return False
        
        # Check horizontal proximity (should be very close)
        gap = word2.x - (word1.x + word1.width)
        if gap > 10:  # More than 10 pixels apart
            return False
        
        # Check vertical alignment
        y_diff = abs(word1.y - word2.y)
        if y_diff > word1.height * 0.3:
            return False
        
        return True
    
    def add_semantic_tags(self, text: str) -> List[str]:
        """
        Add semantic tags to text without removing anything.
        Tags are hints for AI processing.
        """
        tags = []
        
        # Time-related patterns in Khmer
        time_patterns = [
            r'ព្រឹក',      # Morning
            r'ល្ងាច',     # Evening
            r'យប់',       # Night
            r'ថ្ងៃ',       # Day/Noon
            r'មុន\s*បាយ', # Before meal
            r'ក្រោយ\s*បាយ', # After meal
        ]
        
        for pattern in time_patterns:
            if re.search(pattern, text):
                tags.append('time_candidate')
                break
        
        # Quantity patterns
        if re.search(r'\d+\s*(គ្រាប់|ស្លាបព្រា|mg|ml|tab|cap)', text, re.I):
            tags.append('quantity_candidate')
        
        # Medicine name patterns (English)
        if re.search(r'^[A-Z][a-z]+(?:ol|in|ine|ide|ate|cin|fen)e?$', text):
            tags.append('medicine_candidate')
        
        return tags
