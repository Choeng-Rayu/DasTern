#!/usr/bin/env python3
"""
MT5 Demo Script - Test OCR Error Correction

This script demonstrates how to use the MT5 model for OCR correction.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai_corrector import ai_correct, ai_correct_batch, detect_and_correct


def demo_basic_correction():
    """Demo 1: Basic single text correction."""
    print("=" * 60)
    print("DEMO 1: Basic OCR Correction")
    print("=" * 60)
    
    test_cases = [
        ("eng", "paracetamo1 500 rng 2 x daY"),
        ("eng", "amoxici11in 250mg take 3 tirnes dai1y"),
        ("eng", "ibupr0fen 400rng after mea1s"),
        ("khm", "ថ្នាំ បញ្ចុះ កម្ដៅ"),
        ("fra", "comprimé 2x par jour avant 1es repas"),
    ]
    
    for lang, noisy_text in test_cases:
        print(f"\nLanguage: {lang}")
        print(f"Input:    {noisy_text}")
        
        corrected = ai_correct(noisy_text, lang=lang)
        print(f"Output:   {corrected}")
        print("-" * 60)


def demo_batch_processing():
    """Demo 2: Batch processing (more efficient)."""
    print("\n" + "=" * 60)
    print("DEMO 2: Batch Processing")
    print("=" * 60)
    
    # Multiple texts to correct at once
    texts = [
        "paracetamo1 500mg",
        "amoxici11in 250mg",
        "ibupr0fen 400mg",
        "asprin l00mg",
        "metforrn1n 500mg"
    ]
    
    print(f"\nCorrecting {len(texts)} texts in one batch...\n")
    
    corrected_texts = ai_correct_batch(texts, lang="eng")
    
    for original, corrected in zip(texts, corrected_texts):
        print(f"{original:30s} → {corrected}")


def demo_auto_detection():
    """Demo 3: Auto-detect language."""
    print("\n" + "=" * 60)
    print("DEMO 3: Auto Language Detection")
    print("=" * 60)
    
    texts = [
        "asprin l00 mg once dai1y",
        "comprimé matin et s0ir",
    ]
    
    for text in texts:
        print(f"\nInput: {text}")
        result = detect_and_correct(text)
        print(f"Detected Language: {result['detected_language']}")
        print(f"Corrected: {result['corrected']}")
        print("-" * 60)


def demo_parameter_tuning():
    """Demo 4: Different parameter settings."""
    print("\n" + "=" * 60)
    print("DEMO 4: Parameter Tuning")
    print("=" * 60)
    
    text = "paracetamo1 500 rng 2 x daY"
    
    print(f"\nOriginal: {text}\n")
    
    # Test different beam sizes
    for num_beams in [1, 2, 4, 8]:
        corrected = ai_correct(text, lang="eng", num_beams=num_beams)
        print(f"Beams={num_beams}: {corrected}")
    
    print("\nNote: Higher beams = better quality but slower")


def demo_medical_prescriptions():
    """Demo 5: Real prescription-like examples."""
    print("\n" + "=" * 60)
    print("DEMO 5: Medical Prescription Examples")
    print("=" * 60)
    
    prescriptions = [
        "Take 1 tab1et of paracetamo1 500mg 3x daily after mea1s for 5 days",
        "Amoxici11in 250rng capsu1e 2 tirnes dai1y for l week",
        "0meprazole 20mg 0nce daily before breakfast",
        "Metforrn1n 500rng twice a day with mea1s",
    ]
    
    for i, rx in enumerate(prescriptions, 1):
        print(f"\n[Prescription {i}]")
        print(f"Raw OCR:  {rx}")
        corrected = ai_correct(rx, lang="eng", num_beams=4)
        print(f"Corrected: {corrected}")
        print("-" * 60)


def demo_performance_comparison():
    """Demo 6: Performance with/without AI correction."""
    print("\n" + "=" * 60)
    print("DEMO 6: Impact of AI Correction")
    print("=" * 60)
    
    test_texts = [
        "paracetamo1 500 rng",
        "amoxici11in 250rng",
        "take 1 tab1et",
        "3 tirnes dai1y",
        "after mea1s"
    ]
    
    print("\n✅ WITH AI Correction:")
    for text in test_texts:
        corrected = ai_correct(text, lang="eng")
        print(f"  {text:25s} → {corrected}")
    
    print("\n❌ WITHOUT AI Correction (raw OCR errors remain):")
    for text in test_texts:
        print(f"  {text}")


def interactive_mode():
    """Interactive demo - user enters text."""
    print("\n" + "=" * 60)
    print("INTERACTIVE MODE")
    print("=" * 60)
    print("\nEnter OCR text to correct (or 'quit' to exit)")
    print("Format: [lang] text")
    print("Example: eng paracetamo1 500mg")
    print("Languages: eng (English), khm (Khmer), fra (French)")
    print()
    
    while True:
        try:
            user_input = input(">>> ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_input:
                continue
            
            # Parse input
            parts = user_input.split(maxsplit=1)
            if len(parts) < 2:
                print("❌ Format: [lang] text")
                continue
            
            lang = parts[0]
            text = parts[1]
            
            if lang not in ['eng', 'khm', 'fra']:
                print("❌ Language must be: eng, khm, or fra")
                continue
            
            # Correct
            corrected = ai_correct(text, lang=lang)
            print(f"✅ Corrected: {corrected}\n")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("  MT5 OCR Error Correction Demo")
    print("="*60)
    print("\nLoading MT5 model (this may take a moment)...")
    
    try:
        # Pre-load model
        from app.ai_corrector import load_model
        load_model()
        print("✅ Model loaded successfully!\n")
        
        # Run demos
        demo_basic_correction()
        demo_batch_processing()
        demo_auto_detection()
        demo_parameter_tuning()
        demo_medical_prescriptions()
        demo_performance_comparison()
        
        # Optional: Interactive mode
        print("\n" + "="*60)
        response = input("\nRun interactive mode? (y/n): ").strip().lower()
        if response == 'y':
            interactive_mode()
        
        print("\n✅ Demo complete!")
        print("\nFor more information, see: ai/MT5_GUIDE.md")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. Virtual environment is activated")
        print("2. All dependencies are installed")
        print("3. Model files exist or internet connection is available")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
