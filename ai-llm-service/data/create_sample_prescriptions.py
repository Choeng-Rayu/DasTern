import json
import os

def create_prescription_training_data():
    """Create sample_prescriptions.jsonl with few-shot learning examples"""
    
    examples = [
        {
            "user": """វេជ្ជបណ្ឌិត ដោក់ទ័រ ស៊ុន មនីរ័ត្ន
មន្ទីរពេទ្យកាល់ម៉ិត
Tel: 023-123-456

អ្នកជំងឺ: លោក ពេជ្រ ចន្ទ
អាយុ: ៣៥ឆ្នាំ  ភេទ: ប
កាលបរិច្ឆេទ: ២៥/០១/២០២៤

ឱសថកម្មង់:
១. paracetamol 500mg
   Tab i bd x 7days
   
២. amoxicilin 250mg  
   Cap i tds x 5days

៣. ORS sachet
   Sol i prn""",
            
            "assistant": """{
  "patient_name": "លោក ពេជ្រ ចន្ទ",
  "patient_name_romanized": "Mr. Pich Chan", 
  "age": 35,
  "gender": "Male",
  "date": "25/01/2024",
  "prescriber_name": "ដោក់ទ័រ ស៊ុន មនីរ័ត្ន",
  "prescriber_facility": "មន្ទីរពេទ្យកាល់ម៉ិត",
  "prescriber_contact": "023-123-456",
  "medications": [
    {
      "medication_name": "Paracetamol",
      "strength": "500mg",
      "form": "tablet",
      "dosage": "1 tablet",
      "frequency": "twice daily",
      "frequency_times": 2,
      "duration": "7 days",
      "duration_days": 7,
      "instructions_english": "Take 1 tablet twice daily for 7 days",
      "instructions_khmer": "ផឹកថ្នាំ ១គ្រាប់ ២ដង ក្នុងមួយថ្ងៃ រយៈពេល ៧ថ្ងៃ"
    },
    {
      "medication_name": "Amoxicillin", 
      "strength": "250mg",
      "form": "capsule",
      "dosage": "1 capsule",
      "frequency": "three times daily",
      "frequency_times": 3, 
      "duration": "5 days",
      "duration_days": 5,
      "instructions_english": "Take 1 capsule three times daily for 5 days",
      "instructions_khmer": "ផឹកថ្នាំ ១គ្រាប់ ៣ដង ក្នុងមួយថ្ងៃ រយៈពេល ៥ថ្ងៃ"
    },
    {
      "medication_name": "ORS", 
      "strength": "1 sachet",
      "form": "solution",
      "dosage": "1 sachet",
      "frequency": "as needed",
      "frequency_times": 0,
      "duration": "as needed", 
      "duration_days": null,
      "instructions_english": "Dissolve 1 sachet in water, take as needed",
      "instructions_khmer": "រំលាយ ១កញ្ចប់ ក្នុងទឹក ផឹកតាមត្រូវការ"
    }
  ],
  "language_detected": "mixed_khmer_english",
  "confidence_score": 0.94
}"""
        },
        
        {
            "user": """Dr. Sarah Kim, MD
Central Hospital Phnom Penh
License: MD-2024-456

Patient: Miss Sophea Lim
Age: 28  Gender: F  
Date: 26/01/2024

Rx:
1. Ibuprofen 400mg tabs
   Take 1 tab q8h with food
   #21 tabs (7 days)
   
2. Omeprazol 20mg caps
   1 cap od before breakfast  
   #30 caps (1 month)

3. Vitamin B-complex
   1 tab daily with meals
   #30 tabs""",
   
            "assistant": """{
  "patient_name": "Miss Sophea Lim",
  "patient_name_romanized": "Miss Sophea Lim",
  "age": 28,
  "gender": "Female", 
  "date": "26/01/2024",
  "prescriber_name": "Dr. Sarah Kim, MD",
  "prescriber_facility": "Central Hospital Phnom Penh",
  "prescriber_license": "MD-2024-456",
  "prescriber_contact": null,
  "medications": [
    {
      "medication_name": "Ibuprofen",
      "strength": "400mg", 
      "form": "tablet",
      "dosage": "1 tablet",
      "frequency": "every 8 hours",
      "frequency_times": 3,
      "duration": "7 days",
      "duration_days": 7,
      "instructions_english": "Take 1 tablet every 8 hours with food",
      "instructions_khmer": "ផឹកថ្នាំ ១គ្រាប់ រៀងរាល់ ៨ម៉ោង ជាមួយអាហារ"
    },
    {
      "medication_name": "Omeprazole",
      "strength": "20mg",
      "form": "capsule", 
      "dosage": "1 capsule",
      "frequency": "once daily",
      "frequency_times": 1,
      "duration": "30 days",
      "duration_days": 30,
      "instructions_english": "Take 1 capsule once daily before breakfast",
      "instructions_khmer": "ផឹកថ្នាំ ១គ្រាប់ ១ដង ក្នុងមួយថ្ងៃ មុនពេលអាហារព្រឹក"
    },
    {
      "medication_name": "Vitamin B-complex",
      "strength": "standard",
      "form": "tablet",
      "dosage": "1 tablet", 
      "frequency": "once daily",
      "frequency_times": 1,
      "duration": "30 days",
      "duration_days": 30,
      "instructions_english": "Take 1 tablet daily with meals",
      "instructions_khmer": "ផឹកថ្នាំ ១គ្រាប់ ១ដង ក្នុងមួយថ្ងៃ ជាមួយអាហារ"
    }
  ],
  "language_detected": "english",
  "confidence_score": 0.97
}"""
        },

        {
            "user": """រុស្សី គ្លីនិច
Dr. ព្រះករុណា ណន  
ផ្លូវ ២៧១ ភ្នំពេញ

អ្នកជំងឺ: កុមារី ច័ន្ទ ដារ៉ា  
អាយុ: ១២ឆ្នាំ ភេទ: ស្រី
កាលបរិច្ឆេទ: ២៦/០១/២០២៤

ឱសថកម្មង់:
១. ថ្នាំបញ្ចុះកម្ដៅ (paracetamol) ១២០mg/5ml
   ផឹក ៥ml ៣ដង ក្នុងមួយថ្ងៃ រយៈពេល ៣ថ្ងៃ
   
២. ថ្នាំអាម៉ុកស៊ីស៊ីលីន ១២៥mg/5ml  
   ផឹក ៥ml ២ដង ក្នុងមួយថ្ងៃ រយៈពេល ៧ថ្ងៃ""",
   
            "assistant": """{
  "patient_name": "កុមារី ច័ន្ទ ដារ៉ា",
  "patient_name_romanized": "Miss Chan Dara",
  "age": 12,
  "gender": "Female",
  "date": "26/01/2024", 
  "prescriber_name": "Dr. ព្រះករុណា ណន",
  "prescriber_facility": "រុស្សី គ្លីនិច",
  "prescriber_contact": "ផ្លូវ ២៧១ ភ្នំពេញ",
  "medications": [
    {
      "medication_name": "Paracetamol",
      "strength": "120mg/5ml",
      "form": "syrup",
      "dosage": "5ml",
      "frequency": "three times daily", 
      "frequency_times": 3,
      "duration": "3 days",
      "duration_days": 3,
      "instructions_english": "Take 5ml three times daily for 3 days",
      "instructions_khmer": "ផឹក ៥ml ៣ដង ក្នុងមួយថ្ងៃ រយៈពេល ៣ថ្ងៃ"
    },
    {
      "medication_name": "Amoxicillin",
      "strength": "125mg/5ml",
      "form": "syrup", 
      "dosage": "5ml",
      "frequency": "twice daily",
      "frequency_times": 2,
      "duration": "7 days", 
      "duration_days": 7,
      "instructions_english": "Take 5ml twice daily for 7 days",
      "instructions_khmer": "ផឹក ៥ml ២ដង ក្នុងមួយថ្ងៃ រយៈពេល ៧ថ្ងៃ"
    }
  ],
  "language_detected": "khmer", 
  "confidence_score": 0.91
}"""
        }
    ]
    
    return examples

def save_training_dataset():
    """Save as sample_prescriptions.jsonl"""
    examples = create_prescription_training_data()
    
    # Create few-shot learning format
    output_file = "data/training/sample_prescriptions.jsonl"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for example in examples:
            # Standard few-shot format
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    
    print(f"✅ Created {len(examples)} training examples")
    print(f"📁 Saved to: {output_file}")
    print(f"💾 Total file size: {os.path.getsize(output_file)} bytes")
    
    return output_file

if __name__ == "__main__":
    save_training_dataset()