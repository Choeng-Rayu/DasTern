#!/usr/bin/env python3
"""
End-to-End Test Script: OCR → AI → Response Flow
=================================================

This script performs a real end-to-end test:
1. Checks both OCR and AI services are running
2. Sends an image to OCR service for processing
3. Logs the raw OCR output
4. Sends OCR data to AI service for enhancement
5. Validates the AI response
6. Reports total processing time and success/failure

Usage:
    python test_e2e_flow.py [--image PATH]
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime

# Configuration
OCR_SERVICE_URL = os.getenv("OCR_SERVICE_URL", "http://localhost:8000")
AI_SERVICE_URL = os.getenv("AI_LLM_SERVICE_URL", "http://localhost:8001")
DEFAULT_TEST_IMAGE = "/home/rayu/DasTern/OCR_Test_Space/images/image.png"


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def log_step(step: int, message: str, status: str = "INFO"):
    """Log a step with color coding"""
    color = {
        "INFO": Colors.CYAN,
        "SUCCESS": Colors.GREEN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.RED,
        "HEADER": Colors.BOLD
    }.get(status, Colors.RESET)
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] Step {step}: {message}{Colors.RESET}")


def check_services():
    """Check if both services are running"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}CHECKING SERVICES{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    
    services_ok = True
    
    # Check OCR service
    try:
        resp = requests.get(f"{OCR_SERVICE_URL}/api/v1/health", timeout=5)
        if resp.status_code == 200:
            print(f"{Colors.GREEN}✓ OCR Service: Running at {OCR_SERVICE_URL}{Colors.RESET}")
        else:
            print(f"{Colors.RED}✗ OCR Service: Unhealthy (status {resp.status_code}){Colors.RESET}")
            services_ok = False
    except Exception as e:
        print(f"{Colors.RED}✗ OCR Service: Not reachable - {e}{Colors.RESET}")
        services_ok = False
    
    # Check AI service
    try:
        resp = requests.get(f"{AI_SERVICE_URL}/health", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            ollama_ok = data.get("ollama_connected", False)
            if ollama_ok:
                print(f"{Colors.GREEN}✓ AI Service: Running at {AI_SERVICE_URL} (Ollama connected){Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}⚠ AI Service: Running but Ollama not connected{Colors.RESET}")
        else:
            print(f"{Colors.RED}✗ AI Service: Unhealthy (status {resp.status_code}){Colors.RESET}")
            services_ok = False
    except Exception as e:
        print(f"{Colors.RED}✗ AI Service: Not reachable - {e}{Colors.RESET}")
        services_ok = False
    
    # Check Ollama directly
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=5)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            print(f"{Colors.GREEN}✓ Ollama: Running with models: {model_names}{Colors.RESET}")
        else:
            print(f"{Colors.RED}✗ Ollama: Not responding{Colors.RESET}")
            services_ok = False
    except Exception as e:
        print(f"{Colors.RED}✗ Ollama: Not reachable - {e}{Colors.RESET}")
        services_ok = False
    
    return services_ok


def step1_process_ocr(image_path: str):
    """Step 1: Send image to OCR service"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}STEP 1: OCR PROCESSING{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    
    log_step(1, f"Processing image: {image_path}", "INFO")
    
    if not os.path.exists(image_path):
        log_step(1, f"Image not found: {image_path}", "ERROR")
        return None
    
    file_size = os.path.getsize(image_path) / 1024
    log_step(1, f"Image size: {file_size:.1f} KB", "INFO")
    
    start_time = time.time()
    
    try:
        with open(image_path, "rb") as f:
            files = {"file": (os.path.basename(image_path), f, "image/png")}
            response = requests.post(
                f"{OCR_SERVICE_URL}/api/v1/ocr",
                files=files,
                timeout=120
            )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            raw_text_len = len(result.get("raw_text", ""))
            blocks_count = len(result.get("blocks", []))
            
            log_step(1, f"OCR completed in {elapsed:.1f}s", "SUCCESS")
            log_step(1, f"  - Blocks detected: {blocks_count}", "INFO")
            log_step(1, f"  - Raw text length: {raw_text_len} chars", "INFO")
            
            # Show preview of raw text
            raw_text = result.get("raw_text", "")
            if raw_text:
                preview = raw_text[:300] + "..." if len(raw_text) > 300 else raw_text
                print(f"\n{Colors.CYAN}[RAW OCR TEXT PREVIEW]{Colors.RESET}")
                print(f"{preview}\n")
            
            return result
        else:
            log_step(1, f"OCR failed with status {response.status_code}", "ERROR")
            log_step(1, f"  Response: {response.text[:200]}", "ERROR")
            return None
            
    except requests.exceptions.Timeout:
        log_step(1, f"OCR timeout after {time.time() - start_time:.0f}s", "ERROR")
        return None
    except Exception as e:
        log_step(1, f"OCR error: {e}", "ERROR")
        return None


def step2_send_to_ai(ocr_data: dict):
    """Step 2: Send OCR data to AI service for enhancement"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}STEP 2: AI ENHANCEMENT{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    
    log_step(2, "Sending OCR data to AI service...", "INFO")
    log_step(2, f"  Target: {AI_SERVICE_URL}/extract-reminders", "INFO")
    
    start_time = time.time()
    
    try:
        payload = {"raw_ocr_json": ocr_data}
        
        response = requests.post(
            f"{AI_SERVICE_URL}/extract-reminders",
            json=payload,
            timeout=180  # 3 minutes timeout
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            medications = result.get("medications", [])
            success = result.get("success", False)
            
            if success:
                log_step(2, f"AI enhancement completed in {elapsed:.1f}s", "SUCCESS")
                log_step(2, f"  - Medications extracted: {len(medications)}", "INFO")
                
                # Show medication details
                if medications:
                    print(f"\n{Colors.CYAN}[EXTRACTED MEDICATIONS]{Colors.RESET}")
                    for i, med in enumerate(medications, 1):
                        name = med.get("name", "Unknown")
                        dosage = med.get("dosage", "N/A")
                        times = med.get("times", [])
                        print(f"  {i}. {name} - {dosage} - Times: {times}")
                    print()
            else:
                log_step(2, f"AI returned success=false in {elapsed:.1f}s", "WARNING")
                log_step(2, f"  Error: {result.get('error', 'Unknown')}", "WARNING")
            
            return result
        else:
            log_step(2, f"AI failed with status {response.status_code}", "ERROR")
            log_step(2, f"  Response: {response.text[:200]}", "ERROR")
            return None
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        log_step(2, f"AI timeout after {elapsed:.0f}s", "ERROR")
        log_step(2, "  Try increasing OLLAMA_TIMEOUT or using a faster model", "WARNING")
        return None
    except Exception as e:
        log_step(2, f"AI error: {e}", "ERROR")
        return None


def step3_validate_response(ai_result: dict):
    """Step 3: Validate the AI response"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}STEP 3: VALIDATION{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    
    validations = []
    
    # Check success flag
    success = ai_result.get("success", False)
    validations.append(("success flag is True", success))
    
    # Check medications exist
    medications = ai_result.get("medications", [])
    has_medications = len(medications) > 0
    validations.append(("at least one medication extracted", has_medications))
    
    # Check medication structure
    if medications:
        first_med = medications[0]
        has_name = bool(first_med.get("name"))
        has_times = len(first_med.get("times", [])) > 0
        validations.append(("medication has name", has_name))
        validations.append(("medication has times", has_times))
    
    # Print validation results
    all_passed = True
    for check, passed in validations:
        if passed:
            print(f"  {Colors.GREEN}✓ {check}{Colors.RESET}")
        else:
            print(f"  {Colors.RED}✗ {check}{Colors.RESET}")
            all_passed = False
    
    return all_passed


def run_e2e_test(image_path: str):
    """Run the complete end-to-end test"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}END-TO-END TEST: OCR → AI → RESPONSE{Colors.RESET}")
    print(f"{Colors.BOLD}Started at: {datetime.now().isoformat()}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
    
    total_start = time.time()
    
    # Pre-flight check
    if not check_services():
        print(f"\n{Colors.RED}{'='*60}{Colors.RESET}")
        print(f"{Colors.RED}TEST ABORTED: Services not available{Colors.RESET}")
        print(f"{Colors.RED}{'='*60}{Colors.RESET}")
        return False
    
    # Step 1: OCR Processing
    ocr_result = step1_process_ocr(image_path)
    if not ocr_result:
        print(f"\n{Colors.RED}{'='*60}{Colors.RESET}")
        print(f"{Colors.RED}TEST FAILED at Step 1: OCR Processing{Colors.RESET}")
        print(f"{Colors.RED}{'='*60}{Colors.RESET}")
        return False
    
    # Step 2: AI Enhancement
    ai_result = step2_send_to_ai(ocr_result)
    if not ai_result:
        print(f"\n{Colors.RED}{'='*60}{Colors.RESET}")
        print(f"{Colors.RED}TEST FAILED at Step 2: AI Enhancement{Colors.RESET}")
        print(f"{Colors.RED}{'='*60}{Colors.RESET}")
        return False
    
    # Step 3: Validation
    validation_passed = step3_validate_response(ai_result)
    
    total_elapsed = time.time() - total_start
    
    # Final Summary
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}TEST SUMMARY{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
    
    print(f"\n  Total time: {total_elapsed:.1f}s")
    print(f"  OCR result: {'✓ Success' if ocr_result else '✗ Failed'}")
    print(f"  AI result: {'✓ Success' if ai_result else '✗ Failed'}")
    print(f"  Validation: {'✓ Passed' if validation_passed else '✗ Failed'}")
    
    if ocr_result and ai_result and validation_passed:
        print(f"\n{Colors.GREEN}{'='*60}{Colors.RESET}")
        print(f"{Colors.GREEN}✓ END-TO-END TEST PASSED{Colors.RESET}")
        print(f"{Colors.GREEN}  Complete flow: OCR → AI → Response successful!{Colors.RESET}")
        print(f"{Colors.GREEN}{'='*60}{Colors.RESET}")
        return True
    else:
        print(f"\n{Colors.RED}{'='*60}{Colors.RESET}")
        print(f"{Colors.RED}✗ END-TO-END TEST FAILED{Colors.RESET}")
        print(f"{Colors.RED}{'='*60}{Colors.RESET}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="End-to-End OCR → AI Test")
    parser.add_argument(
        "--image", "-i",
        default=DEFAULT_TEST_IMAGE,
        help=f"Path to test image (default: {DEFAULT_TEST_IMAGE})"
    )
    args = parser.parse_args()
    
    success = run_e2e_test(args.image)
    sys.exit(0 if success else 1)
