#!/usr/bin/env python3
"""
Helper Script: Add Training Examples to sample_prescriptions.jsonl

This script helps you easily add new training examples for few-shot learning.
Each example teaches LLaMA how to handle different prescription formats.
"""

import json
import os
from datetime import datetime

TRAINING_FILE = "data/training/sample_prescriptions.jsonl"

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def load_existing_examples():
    """Load existing training examples"""
    if not os.path.exists(TRAINING_FILE):
        return []
    
    examples = []
    with open(TRAINING_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    return examples

def save_example(example):
    """Append new example to training file"""
    os.makedirs(os.path.dirname(TRAINING_FILE), exist_ok=True)
    
    with open(TRAINING_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(example, ensure_ascii=False) + '\n')

def create_example_interactive():
    """Create a new training example interactively"""
    print_header("🎓 Add New Training Example")
    
    print("This will teach LLaMA how to parse a specific prescription format.")
    print("You need to provide:")
    print("  1. Raw OCR text (messy input)")
    print("  2. Expected JSON output (clean, structured)")
    print()
    
    # Get raw OCR text
    print("📝 Step 1: Enter RAW OCR TEXT (messy input)")
    print("Paste the raw OCR text, then press Enter twice:")
    print("-" * 70)
    
    lines = []
    while True:
        line = input()
        if line == "" and len(lines) > 0:
            break
        lines.append(line)
    
    raw_text = "\n".join(lines)
    
    if not raw_text.strip():
        print("❌ No text entered. Cancelled.")
        return None
    
    print(f"\n✅ Raw text captured ({len(raw_text)} characters)")
    print("\nPreview:")
    print("-" * 70)
    print(raw_text[:200] + "..." if len(raw_text) > 200 else raw_text)
    print("-" * 70)
    
    # Get structured output
    print("\n📝 Step 2: Enter EXPECTED JSON OUTPUT (clean, structured)")
    print("Options:")
    print("  1. Paste JSON directly")
    print("  2. Use template (recommended)")
    
    choice = input("\nChoice (1 or 2): ").strip()
    
    if choice == "2":
        # Use template
        print("\n📋 Fill in the template:")
        
        patient_name = input("Patient name (or leave blank): ").strip() or None
        age = input("Patient age: ").strip()
        age = int(age) if age.isdigit() else None
        gender = input("Gender (Male/Female/leave blank): ").strip() or None
        date = input("Date (DD/MM/YYYY or leave blank): ").strip() or None
        doctor = input("Doctor name (or leave blank): ").strip() or None
        hospital = input("Hospital/Clinic name (or leave blank): ").strip() or None
        diagnosis = input("Diagnosis (or leave blank): ").strip() or None
        
        # Medications
        print("\n💊 Medications (enter 'done' when finished):")
        medications = []
        med_num = 1
        
        while True:
            print(f"\n--- Medication {med_num} ---")
            med_name = input(f"  Name: ").strip()
            if med_name.lower() == 'done':
                break
            
            med_strength = input(f"  Strength (e.g., 500mg): ").strip() or None
            med_form = input(f"  Form (tablet/capsule/syrup): ").strip() or "tablet"
            med_dosage = input(f"  Dosage (e.g., 1 tablet): ").strip() or "1 tablet"
            med_freq = input(f"  Frequency (e.g., twice daily): ").strip() or None
            med_duration = input(f"  Duration (e.g., 7 days): ").strip() or None
            
            # Parse frequency times
            freq_times = 0
            if med_freq:
                if "once" in med_freq.lower() or "1x" in med_freq.lower():
                    freq_times = 1
                elif "twice" in med_freq.lower() or "2x" in med_freq.lower():
                    freq_times = 2
                elif "three" in med_freq.lower() or "3x" in med_freq.lower():
                    freq_times = 3
                elif "four" in med_freq.lower() or "4x" in med_freq.lower():
                    freq_times = 4
            
            # Parse duration days
            duration_days = None
            if med_duration:
                import re
                match = re.search(r'(\d+)', med_duration)
                if match:
                    duration_days = int(match.group(1))
            
            medication = {
                "medication_name": med_name,
                "strength": med_strength,
                "form": med_form,
                "dosage": med_dosage,
                "frequency": med_freq,
                "frequency_times": freq_times,
                "duration": med_duration,
                "duration_days": duration_days,
                "instructions_english": f"Take {med_dosage} {med_freq}" if med_freq else f"Take {med_dosage}",
                "instructions_khmer": f"ផឹកថ្នាំ {med_dosage}"
            }
            
            # Remove None values
            medication = {k: v for k, v in medication.items() if v is not None}
            medications.append(medication)
            med_num += 1
        
        # Build structured output
        structured_output = {}
        if patient_name:
            structured_output["patient_name"] = patient_name
        if age:
            structured_output["age"] = age
        if gender:
            structured_output["gender"] = gender
        if date:
            structured_output["date"] = date
        if doctor:
            structured_output["prescriber_name"] = doctor
        if hospital:
            structured_output["prescriber_facility"] = hospital
        if diagnosis:
            structured_output["diagnosis"] = diagnosis
        
        structured_output["medications"] = medications
        structured_output["language_detected"] = "mixed_khmer_english"
        structured_output["confidence_score"] = 0.90
        
        json_output = json.dumps(structured_output, indent=2, ensure_ascii=False)
        
    else:
        # Paste JSON directly
        print("\nPaste JSON output, then press Enter twice:")
        print("-" * 70)
        
        json_lines = []
        while True:
            line = input()
            if line == "" and len(json_lines) > 0:
                break
            json_lines.append(line)
        
        json_output = "\n".join(json_lines)
        
        # Validate JSON
        try:
            json.loads(json_output)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            return None
    
    print("\n✅ JSON output captured")
    print("\nPreview:")
    print("-" * 70)
    preview = json_output[:300] + "..." if len(json_output) > 300 else json_output
    print(preview)
    print("-" * 70)
    
    # Confirm
    confirm = input("\n💾 Save this training example? (yes/no): ").strip().lower()
    
    if confirm in ['yes', 'y']:
        example = {
            "user": raw_text,
            "assistant": json_output
        }
        return example
    else:
        print("❌ Cancelled.")
        return None

def show_quick_add_examples():
    """Show quick examples for common hospital formats"""
    print_header("🚀 Quick Add: Common Hospital Formats")
    
    templates = {
        "1": {
            "name": "Khmer-Soviet Friendship Hospital (Messy OCR)",
            "user": "oviet Friendship Hospital\nHAKF123456\nPatient: 25 years\nChronic condition\nParacetamo1 s00mg\nAmox1cillin 250mg\nTake twice daily",
            "assistant": '{\n  "age": 25,\n  "prescriber_facility": "Khmer-Soviet Friendship Hospital",\n  "medications": [\n    {"medication_name": "Paracetamol", "strength": "500mg"},\n    {"medication_name": "Amoxicillin", "strength": "250mg", "frequency": "twice daily"}\n  ]\n}'
        },
        "2": {
            "name": "Calmette Hospital (Khmer)",
            "user": "មន្ទីរពេទ្យកាល់ម៉ិត\nអ្នកជំងឺ: សុខា\nអាយុ: 30\nថ្នាំ paracetamol 500mg\n1 គ្រាប់ 2ដង",
            "assistant": '{\n  "patient_name": "សុខា",\n  "age": 30,\n  "prescriber_facility": "មន្ទីរពេទ្យកាល់ម៉ិត",\n  "medications": [\n    {"medication_name": "Paracetamol", "strength": "500mg", "frequency": "twice daily"}\n  ]\n}'
        },
        "3": {
            "name": "Custom (Manual Entry)",
            "custom": True
        }
    }
    
    print("Choose a template:")
    for key, template in templates.items():
        print(f"  {key}. {template['name']}")
    
    choice = input("\nChoice: ").strip()
    
    if choice in templates:
        template = templates[choice]
        
        if template.get('custom'):
            return create_example_interactive()
        else:
            print(f"\n📋 Template: {template['name']}")
            print("\nRAW OCR TEXT:")
            print("-" * 70)
            print(template['user'])
            print("-" * 70)
            print("\nEXPECTED JSON OUTPUT:")
            print("-" * 70)
            print(template['assistant'])
            print("-" * 70)
            
            confirm = input("\n💾 Add this example? (yes/no): ").strip().lower()
            
            if confirm in ['yes', 'y']:
                return {
                    "user": template['user'],
                    "assistant": template['assistant']
                }
    
    return None

def main():
    print_header("🎓 Training Example Manager")
    
    # Show existing examples count
    existing = load_existing_examples()
    print(f"📊 Current training examples: {len(existing)}")
    print(f"📁 Training file: {TRAINING_FILE}\n")
    
    print("Options:")
    print("  1. Add new example (interactive)")
    print("  2. Quick add (from templates)")
    print("  3. View existing examples")
    print("  4. Exit")
    
    choice = input("\nChoice: ").strip()
    
    if choice == "1":
        example = create_example_interactive()
        if example:
            save_example(example)
            print(f"\n✅ Training example added! Total: {len(existing) + 1}")
            print(f"📁 Saved to: {TRAINING_FILE}")
    
    elif choice == "2":
        example = show_quick_add_examples()
        if example:
            save_example(example)
            print(f"\n✅ Training example added! Total: {len(existing) + 1}")
            print(f"📁 Saved to: {TRAINING_FILE}")
    
    elif choice == "3":
        print_header("📚 Existing Training Examples")
        for i, ex in enumerate(existing, 1):
            print(f"\n--- Example {i} ---")
            print(f"Input preview: {ex['user'][:100]}...")
            print(f"Output preview: {ex['assistant'][:100]}...")
    
    elif choice == "4":
        print("👋 Goodbye!")
        return
    
    # Ask to add another
    if choice in ["1", "2"]:
        another = input("\n➕ Add another example? (yes/no): ").strip().lower()
        if another in ['yes', 'y']:
            main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
