# Healthcare LNP Model Usage Guide

## Overview
The Healthcare LNP (Language Neural Processing) model is trained to predict diseases and suggest medications based on medical text input. It's a multi-task learning model that provides disease classification, medication recommendations, severity assessment, and risk scoring.

## Model Features

### 1. **Disease Classification**
- Predicts one of 10 disease categories:
  - Cardiovascular
  - Respiratory
  - Gastrointestinal
  - Neurological
  - Musculoskeletal
  - Infectious
  - Metabolic
  - Dermatological
  - Mental Health
  - Other

### 2. **Medication Recommendation**
- Suggests up to 5 common medications based on the diagnosed disease
- 20 supported medications: Aspirin, Metformin, Lisinopril, Atorvastatin, Levothyroxine, etc.

### 3. **Severity Assessment**
- Rates severity as: Mild, Moderate, or Severe

### 4. **Risk Scoring**
- Provides a risk score (0-1) indicating overall patient risk level

### 5. **Symptom Extraction**
- Identifies key symptoms from medical text

---

## How to Use the Model

### Method 1: Direct Python Usage (Recommended)

```python
from healthcare_lnp import HealthcarePredictor

# Load the trained model
predictor = HealthcarePredictor('healthcare_lnp_model.pth')

# Prepare medical text
medical_text = """
65 year old male presenting with chest pain and shortness of breath. 
Medical history includes hypertension and diabetes. 
Vital signs: BP 150/95, HR 110, Temp 37.2C.
"""

# Get predictions
result = predictor.predict(medical_text)

# Access results
print(f"Disease: {result['disease_prediction']}")
print(f"Confidence: {result['disease_confidence']:.2%}")
print(f"Medications: {result['suggested_medications']}")
print(f"Severity: {result['severity_assessment']}")
print(f"Risk Score: {result['risk_score']:.2%}")
```

### Method 2: Using the Main Script

Run the complete training and inference pipeline:

```bash
python healthcare_lnp.py
```

This will:
1. Train a new model on 2000 synthetic medical records
2. Save the trained model as `healthcare_lnp_model.pth`
3. Test the model on 3 sample cases
4. Display predictions and metrics

### Method 3: Web Interface (Streamlit)

Create a `app.py` file with:

```python
import streamlit as st
from healthcare_lnp import HealthcarePredictor

st.title("Healthcare LNP Model - Medical Text Analysis")

# Load model
predictor = HealthcarePredictor('healthcare_lnp_model.pth')

# Input medical text
medical_text = st.text_area("Enter patient medical record:", height=200)

if st.button("Analyze"):
    if medical_text:
        result = predictor.predict(medical_text)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Predicted Disease", result['disease_prediction'])
            st.metric("Confidence", f"{result['disease_confidence']:.2%}")
            st.metric("Risk Score", f"{result['risk_score']:.2%}")
        
        with col2:
            st.metric("Severity", result['severity_assessment'])
            st.write("**Suggested Medications:**")
            for med in result['suggested_medications']:
                st.write(f"- {med}")
```

Run with:
```bash
streamlit run app.py
```

---

## Input Format Requirements

The model expects medical text containing:
- **Patient demographics**: Age, gender
- **Vital signs**: Blood pressure, heart rate, temperature
- **Chief complaint**: Main symptoms
- **Medical history**: Past conditions or medications
- **Physical examination findings**: Relevant exam results

**Example Input:**
```
32 year old female with persistent cough and fever for 5 days. 
Temperature 38.8C. Chest exam reveals bilateral crackles. 
No significant medical history. Chest X-ray shows pneumonia.
```

---

## Output Format

The `predict()` method returns a dictionary with:

```python
{
    'disease_prediction': str,           # Predicted disease category
    'disease_confidence': float,         # Confidence (0-1)
    'suggested_medications': list,       # List of recommended drugs
    'severity_assessment': str,          # 'Mild', 'Moderate', or 'Severe'
    'risk_score': float,                 # Risk level (0-1)
    'symptoms_identified': list          # Extracted symptoms
}
```

---

## Performance Metrics

The model is evaluated on:
- **Accuracy**: Percentage of correct disease predictions
- **Precision**: Accuracy of positive predictions
- **Recall**: Coverage of actual positives
- **F1-Score**: Balanced measure of precision and recall

Typical metrics after training on synthetic data:
- Accuracy: ~85-95% (varies based on training data quality)
- F1-Score: ~0.85-0.92

---

## Configuration

Modify the model behavior in `HealthcareLNPConfig`:

```python
class HealthcareLNPConfig:
    model_name = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"
    max_length = 256              # Max input text length
    batch_size = 16               # Training batch size
    learning_rate = 2e-5          # Optimizer learning rate
    epochs = 10                   # Training epochs
    num_classes = 10              # Number of disease categories
    hidden_dropout_prob = 0.1     # Dropout rate
```

---

## Troubleshooting

### Issue: "Model file not found"
**Solution**: Ensure you've trained and saved the model first:
```bash
python healthcare_lnp.py
```

### Issue: "Read timed out" from HuggingFace
**Solution**: Use a local copy of the model or increase timeout:
```python
from transformers import AutoTokenizer, AutoModel
tokenizer = AutoTokenizer.from_pretrained(
    "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext",
    timeout=30  # Increase timeout
)
```

### Issue: Low confidence predictions
**Solution**: Provide more detailed medical information in the input text

---

## Advanced Usage

### Fine-tuning on Custom Data

```python
from healthcare_lnp import HealthcareLNPConfig, HealthcareLNP, HealthcareAITrainer
import pandas as pd

# Load your custom medical data
df = pd.read_csv('your_medical_data.csv')

config = HealthcareLNPConfig()
model = HealthcareLNP(config)
tokenizer = AutoTokenizer.from_pretrained(config.model_name)

# Prepare datasets
train_dataset, val_dataset = MedicalDataProcessor.prepare_datasets(
    df, tokenizer, config.max_length
)

# Train
trainer = HealthcareAITrainer(model, config, tokenizer)
trainer.train(train_dataloader, val_dataloader)
```

### Batch Inference

```python
medical_texts = [text1, text2, text3, ...]
predictor = HealthcarePredictor('healthcare_lnp_model.pth')

results = []
for text in medical_texts:
    result = predictor.predict(text)
    results.append(result)
```

---

## Notes

- The model uses the **BiomedNLP-PubMedBERT** transformer, trained on biomedical literature
- It's designed for educational/research purposes
- Real-world medical diagnosis requires professional validation
- Always consult with healthcare professionals for actual patient care

---

## Support & Issues

For issues or questions:
1. Check that all required packages are installed: `pip install -r requirements.txt`
2. Ensure the model file `healthcare_lnp_model.pth` exists
3. Verify PyTorch and transformers are properly installed
