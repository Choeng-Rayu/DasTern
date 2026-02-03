#!/usr/bin/env python3
"""
Test AI enhancement with raw OCR data and save prescription to Flutter storage format
"""
import requests
import json
import time
from datetime import datetime
import os

# Raw OCR data from prescription
OCR_DATA = {
  "meta": {
    "languages": [
      "eng",
      "khm",
      "fra"
    ],
    "dpi": 71,
    "processing_time_ms": 2297.294855117798,
    "model_version": "default",
    "stage_times": {
      "validation": 64.26048278808594,
      "quality_analysis": 88.61684799194336,
      "preprocessing": 21.997451782226562,
      "layout_analysis": 141.10302925109863,
      "ocr_extraction": 1978.5821437835693,
      "postprocessing": 2.292156219482422
    },
    "image_size": {
      "width": 972,
      "height": 1280
    }
  },
  "quality": {
    "blur": "low",
    "blur_score": 1382.5243148316551,
    "contrast": "ok",
    "contrast_score": 35.83946881268386,
    "skew_angle": -0.7417594929876797,
    "dpi": 71,
    "is_grayscale": False
  },
  "blocks": [
    {
      "type": "text",
      "bbox": {
        "x": 0,
        "y": 0,
        "width": 988,
        "height": 1292
      },
      "lines": [
        {
          "text": "LPS 2 |",
          "bbox": {
            "x": 192,
            "y": 20,
            "width": 796,
            "height": 35
          },
          "confidence": 0.58,
          "language": "en",
          "tags": []
        },
        {
          "text": "SS",
          "bbox": {
            "x": 180,
            "y": 50,
            "width": 99,
            "height": 18
          },
          "confidence": 0.34,
          "language": "en",
          "tags": []
        },
        {
          "text": "to មន្ទរពហុព្យាបាល សុខ GENS",
          "bbox": {
            "x": 166,
            "y": 53,
            "width": 566,
            "height": 46
          },
          "confidence": 0.6525,
          "language": "kh",
          "tags": []
        },
        {
          "text": "; ets 4 SOK HENG POLYCLINIC",
          "bbox": {
            "x": 168,
            "y": 91,
            "width": 540,
            "height": 32
          },
          "confidence": 0.64,
          "language": "en",
          "tags": []
        },
        {
          "text": "ONF PS] ផ្ទះលេខ235 ភូមិព្រៃទា សង្កាត់ចោមចៅទី3 ខណ្ឌពោធិ៍សែនជ័យ រាជធានីភ្នំពេញ",
          "bbox": {
            "x": 170,
            "y": 119,
            "width": 634,
            "height": 29
          },
          "confidence": 0.7314285714285714,
          "language": "kh",
          "tags": []
        },
        {
          "text": "ENG PO ginig: 089/098 688 685",
          "bbox": {
            "x": 189,
            "y": 143,
            "width": 457,
            "height": 20
          },
          "confidence": 0.8266666666666667,
          "language": "en",
          "tags": []
        },
        {
          "text": "វេជ្ជបញ្ជា",
          "bbox": {
            "x": 430,
            "y": 221,
            "width": 140,
            "height": 37
          },
          "confidence": 0.67,
          "language": "kh",
          "tags": []
        },
        {
          "text": "ឈ្មោះៈ Sk ONU ens: sr ឆ្នាំ កាលបរិច្ឆេទ: 05/01/2026 BAG",
          "bbox": {
            "x": 29,
            "y": 274,
            "width": 921,
            "height": 59
          },
          "confidence": 0.5433333333333333,
          "language": "kh",
          "tags": []
        },
        {
          "text": "១« ri -",
          "bbox": {
            "x": 80,
            "y": 275,
            "width": 308,
            "height": 23
          },
          "confidence": 0.21,
          "language": "en",
          "tags": []
        },
        {
          "text": "INVONS: VHPANNVSo ខណ្ឌ លខកូន អ្នកដំនី: P25000720 ម",
          "bbox": {
            "x": 33,
            "y": 306,
            "width": 917,
            "height": 49
          },
          "confidence": 0.45285714285714285,
          "language": "kh",
          "tags": []
        },
        {
          "text": "ពច រានធានភ្នពេញ លខកូន ប.ស.ល.: 0891509 ក",
          "bbox": {
            "x": 33,
            "y": 340,
            "width": 915,
            "height": 39
          },
          "confidence": 0.635,
          "language": "kh",
          "tags": []
        },
        {
          "text": "6រាសិនិច្ឆ័យៈ 1534 - Asthénie",
          "bbox": {
            "x": 34,
            "y": 370,
            "width": 264,
            "height": 32
          },
          "confidence": 0.6975,
          "language": "kh",
          "tags": []
        },
        {
          "text": "កា",
          "bbox": {
            "x": 35,
            "y": 435,
            "width": 920,
            "height": 59
          },
          "confidence": 0.29,
          "language": "kh",
          "tags": []
        },
        {
          "text": "យយ",
          "bbox": {
            "x": 35,
            "y": 487,
            "width": 865,
            "height": 67
          },
          "confidence": 0.0,
          "language": "kh",
          "tags": []
        },
        {
          "text": "ពយា",
          "bbox": {
            "x": 9,
            "y": 545,
            "width": 954,
            "height": 69
          },
          "confidence": 0.0,
          "language": "kh",
          "tags": []
        },
        {
          "text": "- TA:100/65 mmHg,",
          "bbox": {
            "x": 59,
            "y": 724,
            "width": 182,
            "height": 20
          },
          "confidence": 0.83,
          "language": "en",
          "tags": []
        },
        {
          "text": "- P:90 /min",
          "bbox": {
            "x": 58,
            "y": 752,
            "width": 107,
            "height": 18
          },
          "confidence": 0.8633333333333333,
          "language": "en",
          "tags": []
        },
        {
          "text": "- T°: 36,7°C",
          "bbox": {
            "x": 59,
            "y": 783,
            "width": 107,
            "height": 18
          },
          "confidence": 0.68,
          "language": "en",
          "tags": []
        },
        {
          "text": "គ្រូពេខ្យព្យាអាល",
          "bbox": {
            "x": 735,
            "y": 846,
            "width": 119,
            "height": 23
          },
          "confidence": 0.11,
          "language": "kh",
          "tags": []
        },
        {
          "text": "នលើ ory. អម រស្មី",
          "bbox": {
            "x": 272,
            "y": 942,
            "width": 575,
            "height": 32
          },
          "confidence": 0.4825,
          "language": "kh",
          "tags": []
        },
        {
          "text": "| សូមយក៖វជ្ជបញ្ជាមកអាមួយ ពេលព័នត្យ្ឃលើក6ក្រាយ។",
          "bbox": {
            "x": 4,
            "y": 962,
            "width": 400,
            "height": 34
          },
          "confidence": 0.3333333333333333,
          "language": "kh",
          "tags": []
        },
        {
          "text": "|",
          "bbox": {
            "x": 971,
            "y": 1284,
            "width": 1,
            "height": 8
          },
          "confidence": 0.82,
          "language": None,
          "tags": []
        }
      ],
      "raw_text": "LPS 2 |\nSS\nto មន្ទរពហុព្យាបាល សុខ GENS\n; ets 4 SOK HENG POLYCLINIC\nONF PS] ផ្ទះលេខ235 ភូមិព្រៃទា សង្កាត់ចោមចៅទី3 ខណ្ឌពោធិ៍សែនជ័យ រាជធានីភ្នំពេញ\nENG PO ginig: 089/098 688 685\nវេជ្ជបញ្ជា\nឈ្មោះៈ Sk ONU ens: sr ឆ្នាំ កាលបរិច្ឆេទ: 05/01/2026 BAG\n១« ri -\nINVONS: VHPANNVSo ខណ្ឌ លខកូន អ្នកដំនី: P25000720 ម\nពច រានធានភ្នពេញ លខកូន ប.ស.ល.: 0891509 ក\n6រាសិនិច្ឆ័យៈ 1534 - Asthénie\nកា\nយយ\nពយា\n- TA:100/65 mmHg,\n- P:90 /min\n- T°: 36,7°C\nគ្រូពេខ្យព្យាអាល\nនលើ ory. អម រស្មី\n| សូមយក៖វជ្ជបញ្ជាមកអាមួយ ពេលព័នត្យ្ឃលើក6ក្រាយ។\n|"
    }
  ],
  "full_text": "",
  "success": False,
  "error": None
}

def simplify_ocr_data(ocr_data):
    """Simplify OCR data to reduce payload size"""
    simplified = {
        "text": ocr_data.get("blocks", [{}])[0].get("raw_text", ""),
        "languages": ocr_data.get("meta", {}).get("languages", []),
        "quality": ocr_data.get("quality", {})
    }
    return simplified

def send_to_ai_service(ocr_data, timeout=600):
    """Send OCR data to AI service for enhancement"""
    ai_service_url = "http://localhost:8001/extract-reminders"
    
    payload = {
        "raw_ocr_json": ocr_data
    }
    
    print("📤 Sending to AI service:", ai_service_url)
    print(f"⏱️  Timeout: {timeout}s")
    print(f"📊 Payload size: {len(json.dumps(payload))} bytes")
    print()
    
    try:
        start_time = time.time()
        response = requests.post(
            ai_service_url,
            json=payload,
            timeout=timeout
        )
        elapsed = time.time() - start_time
        
        print(f"✅ Response received in {elapsed:.2f}s (Status: {response.status_code})")
        print()
        
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return None
            
    except requests.Timeout:
        print(f"❌ TIMEOUT after {timeout}s")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def save_prescription_to_flutter(ai_result, ocr_data):
    """Save the prescription in Flutter storage format"""
    
    # Create prescription data folder if needed
    data_folder = "/home/rayu/DasTern/ocr_ai_for_reminder/data"
    os.makedirs(data_folder, exist_ok=True)
    
    # Generate prescription ID
    timestamp_ms = int(time.time() * 1000)
    prescription_id = str(timestamp_ms)
    
    # Parse medications from AI result
    medications = []
    if ai_result and "medications" in ai_result:
        for med in ai_result["medications"]:
            medication = {
                "name": med.get("name", "Unknown"),
                "dosage": med.get("dosage", ""),
                "times": med.get("times", []),
                "times24h": med.get("times24h", []),
                "repeat": med.get("repeat", "daily"),
                "durationDays": med.get("duration_days", 7),
                "notes": med.get("notes", "")
            }
            medications.append(medication)
    
    # Create prescription data
    prescription_data = {
        "id": prescription_id,
        "createdAt": datetime.now().isoformat(),
        "medications": medications,
        "patientName": "Patient",
        "age": 35,
        "diagnosis": "Asthénie",
        "rawOcrData": OCR_DATA,
        "aiMetadata": {
            "model": ai_result.get("model", "llama3.2:3b") if ai_result else None,
            "processingTime": ai_result.get("processing_time_ms", 0) if ai_result else 0,
            "confidence": ai_result.get("confidence", 0) if ai_result else 0
        }
    }
    
    # Load existing prescriptions or create new list
    prescriptions_file = f"{data_folder}/prescriptions.json"
    
    if os.path.exists(prescriptions_file):
        with open(prescriptions_file, 'r') as f:
            prescriptions_list = json.load(f)
    else:
        prescriptions_list = []
    
    # Add new prescription
    prescriptions_list.append(prescription_data)
    
    # Save prescriptions
    with open(prescriptions_file, 'w') as f:
        json.dump(prescriptions_list, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Prescription saved to: {prescriptions_file}")
    print(f"   ID: {prescription_id}")
    print(f"   Medications: {len(medications)}")
    
    return prescription_data

def main():
    print("=" * 70)
    print("🧪 Testing AI Enhancement with Raw OCR Data")
    print("=" * 70)
    print()
    
    # Send to AI service
    print("📋 Step 1: Sending OCR data to AI service...")
    print()
    ai_result = send_to_ai_service(OCR_DATA, timeout=600)
    
    if not ai_result:
        print("❌ AI enhancement failed")
        return
    
    print("📝 AI Result:")
    print(json.dumps(ai_result, indent=2, ensure_ascii=False)[:500] + "...")
    print()
    
    # Save to Flutter storage
    print("📋 Step 2: Saving prescription to Flutter storage...")
    print()
    prescription = save_prescription_to_flutter(ai_result, OCR_DATA)
    
    print()
    print("=" * 70)
    print("✅ Complete! Prescription saved and ready to display in Flutter")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Run Flutter app: flutter run -d linux")
    print("2. Click 'View Saved Prescriptions' on home screen")
    print("3. You should see the newly created prescription")
    print()

if __name__ == "__main__":
    main()
