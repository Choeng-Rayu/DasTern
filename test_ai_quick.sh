#!/bin/bash
# Quick test of AI enhancement with real prescription

echo "Testing AI enhancement with real Khmer prescription..."
echo "This will take 20-90 seconds..."
echo ""

curl -X POST http://localhost:8001/extract-reminders \
  -H "Content-Type: application/json" \
  -d @- <<'EOF' | python3 -m json.tool
{
  "raw_ocr_json": {
    "blocks": [
      {
        "type": "text",
        "lines": [
          {"text": "លេខកូដ: HAKF1354164 ឈ្មោះអ្នកជំងឺ: ង៉ាំ ដានី អាយុ: 19 ឆ្នាំ"},
          {"text": "រោគវិនិច្ឆ័យ : 1. Chronic Cystitis"},
          {"text": "2. Encour ménorhée"},
          {"text": "Esome 20mg |7 គ្រាប់ស្រោប| PO |គ្រាប់ ក្រោយបាយ"}
        ],
        "raw_text": "Patient: ង៉ាំ ដានី, Age: 19, Female\nDiagnosis: Chronic Cystitis\nEsome 20mg 7 capsules PO after meals"
      }
    ],
    "raw_text": "Patient: ង៉ាំ ដានី, Age: 19\nDiagnosis: Chronic Cystitis\nMedication: Esome 20mg, 7 capsules, PO, after meals"
  }
}
EOF

echo ""
echo "Test complete!"
