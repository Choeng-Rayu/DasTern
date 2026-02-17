# healthcare_lnp.py
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import AutoTokenizer, AutoModel, get_linear_schedule_with_warmup
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import json
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class HealthcareLNPConfig:
    """Configuration for Healthcare LNP Model"""
    def __init__(self):
        self.model_name = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"
        self.max_length = 256
        self.batch_size = 16
        self.learning_rate = 2e-5
        self.epochs = 10
        self.num_classes = 10  # Can be adjusted based on disease categories
        self.hidden_dropout_prob = 0.1
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class PatientDataset(Dataset):
    """Dataset for patient medical records"""
    def __init__(self, texts, labels, tokenizer, max_length):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class HealthcareLNP(nn.Module):
    """Healthcare Language Neural Processing Model"""
    def __init__(self, config: HealthcareLNPConfig):
        super(HealthcareLNP, self).__init__()
        self.config = config
        self.bert = AutoModel.from_pretrained(config.model_name)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        
        # Multi-task heads
        self.disease_classifier = nn.Linear(self.bert.config.hidden_size, config.num_classes)
        self.medication_predictor = nn.Linear(self.bert.config.hidden_size, 50)  # 50 common medications
        self.severity_predictor = nn.Linear(self.bert.config.hidden_size, 3)  # Mild, Moderate, Severe
        
        # Additional layers for medical concept understanding
        self.symptom_extractor = nn.Sequential(
            nn.Linear(self.bert.config.hidden_size, 256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, 100)  # 100 common symptoms
        )
        
        # Risk assessment
        self.risk_assessor = nn.Sequential(
            nn.Linear(self.bert.config.hidden_size, 128),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )
    
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_dict=True
        )
        
        pooled_output = outputs.pooler_output
        pooled_output = self.dropout(pooled_output)
        
        # Get predictions from all heads
        disease_pred = self.disease_classifier(pooled_output)
        medication_pred = self.medication_predictor(pooled_output)
        severity_pred = self.severity_predictor(pooled_output)
        symptoms = self.symptom_extractor(pooled_output)
        risk_score = self.risk_assessor(pooled_output)
        
        return {
            'disease': disease_pred,
            'medication': medication_pred,
            'severity': severity_pred,
            'symptoms': symptoms,
            'risk_score': risk_score
        }

class HealthcareAITrainer:
    """Trainer for Healthcare LNP Model"""
    def __init__(self, model, config, tokenizer):
        self.model = model.to(config.device)
        self.config = config
        self.tokenizer = tokenizer
        self.optimizer = AdamW(model.parameters(), lr=config.learning_rate)
        
    def train(self, train_dataloader, val_dataloader):
        """Training loop"""
        self.model.train()
        total_steps = len(train_dataloader) * self.config.epochs
        
        scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=0,
            num_training_steps=total_steps
        )
        
        for epoch in range(self.config.epochs):
            print(f"\nEpoch {epoch + 1}/{self.config.epochs}")
            total_loss = 0
            
            for batch_idx, batch in enumerate(train_dataloader):
                input_ids = batch['input_ids'].to(self.config.device)
                attention_mask = batch['attention_mask'].to(self.config.device)
                labels = batch['labels'].to(self.config.device)
                
                self.optimizer.zero_grad()
                
                outputs = self.model(input_ids, attention_mask)
                
                # Multi-task loss calculation
                loss_disease = nn.CrossEntropyLoss()(outputs['disease'], labels)
                loss_medication = nn.BCEWithLogitsLoss()(outputs['medication'], 
                                                        torch.zeros_like(outputs['medication']))  # Placeholder
                loss_severity = nn.CrossEntropyLoss()(outputs['severity'], 
                                                     labels % 3)  # Placeholder logic
                
                # Weighted total loss
                total_batch_loss = (0.5 * loss_disease + 0.3 * loss_medication + 0.2 * loss_severity)
                total_batch_loss.backward()
                
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.optimizer.step()
                scheduler.step()
                
                total_loss += total_batch_loss.item()
                
                if batch_idx % 10 == 0:
                    print(f"Batch {batch_idx}, Loss: {total_batch_loss.item():.4f}")
            
            avg_train_loss = total_loss / len(train_dataloader)
            print(f"Average training loss: {avg_train_loss:.4f}")
            
            # Validate
            self.evaluate(val_dataloader)
    
    def evaluate(self, dataloader):
        """Evaluation function"""
        self.model.eval()
        predictions = []
        true_labels = []
        
        with torch.no_grad():
            for batch in dataloader:
                input_ids = batch['input_ids'].to(self.config.device)
                attention_mask = batch['attention_mask'].to(self.config.device)
                labels = batch['labels'].to(self.config.device)
                
                outputs = self.model(input_ids, attention_mask)
                _, preds = torch.max(outputs['disease'], dim=1)
                
                predictions.extend(preds.cpu().numpy())
                true_labels.extend(labels.cpu().numpy())
        
        accuracy = accuracy_score(true_labels, predictions)
        precision = precision_score(true_labels, predictions, average='weighted')
        recall = recall_score(true_labels, predictions, average='weighted')
        f1 = f1_score(true_labels, predictions, average='weighted')
        
        print(f"\nValidation Metrics:")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"F1-Score: {f1:.4f}")
        
        self.model.train()
        
        return accuracy, f1

class MedicalDataProcessor:
    """Process medical data for training"""
    
    DISEASE_CATEGORIES = {
        0: "Cardiovascular",
        1: "Respiratory",
        2: "Gastrointestinal",
        3: "Neurological",
        4: "Musculoskeletal",
        5: "Infectious",
        6: "Metabolic",
        7: "Dermatological",
        8: "Mental Health",
        9: "Other"
    }
    
    COMMON_MEDICATIONS = [
        "Aspirin", "Metformin", "Lisinopril", "Atorvastatin", "Levothyroxine",
        "Amlodipine", "Metoprolol", "Albuterol", "Omeprazole", "Losartan",
        "Simvastatin", "Hydrochlorothiazide", "Azithromycin", "Prednisone",
        "Gabapentin", "Fluoxetine", "Warfarin", "Insulin", "Furosemide", "Ibuprofen",
        "Amoxicillin", "Ciprofloxacin", "Ranitidine", "Clotrimazole", "Paracetamol",
        "Clopidogrel", "Enalapril", "Nitrates", "Digoxin", "Diltiazem",
        "Atenolol", "Propranolol", "Verapamil", "Hydralazine", "Minoxidil",
        "Spironolactone", "Amiloride", "Acetazolamide", "Thiazide", "Torsemide",
        "Doxycycline", "Erythromycin", "Tetracycline", "Penicillin", "Cephalexin",
        "Metronidazole", "Fluconazole", "Ketoconazole", "Griseofulvin", "Acyclovir"
    ]
    
    @staticmethod
    def create_sample_data(num_samples=1000):
        """Create synthetic medical data for training"""
        np.random.seed(42)
        
        data = []
        for i in range(num_samples):
            # Generate patient demographics
            age = np.random.randint(18, 90)
            gender = np.random.choice(['Male', 'Female'])
            
            # Random disease category
            disease_cat = np.random.randint(0, 10)
            disease = MedicalDataProcessor.DISEASE_CATEGORIES[disease_cat]
            
            # Create medical text
            symptoms = np.random.choice([
                "fever and cough", "chest pain", "headache", "fatigue",
                "shortness of breath", "nausea", "joint pain", "rash",
                "dizziness", "abdominal pain"
            ], size=np.random.randint(1, 4), replace=False)
            
            # Select medications
            meds = np.random.choice(
                MedicalDataProcessor.COMMON_MEDICATIONS,
                size=np.random.randint(1, 4),
                replace=False
            )
            
            # Create medical record text
            text = f"""
            Patient: {gender}, {age} years old.
            Presenting symptoms: {', '.join(symptoms)}.
            Medical history: {np.random.choice(['Hypertension', 'Diabetes', 'Asthma', 'None'])}.
            Vital signs: BP {np.random.randint(110, 160)}/{np.random.randint(70, 100)}, 
            HR {np.random.randint(60, 100)}, Temp {np.random.uniform(36.5, 39.0):.1f}C.
            Suspected condition: {disease}.
            Prescribed medications: {', '.join(meds)}.
            Treatment plan: {np.random.choice(['Outpatient care', 'Hospital admission', 'Follow-up in 1 week'])}.
            """
            
            data.append({
                'text': text,
                'disease_category': disease_cat,
                'age': age,
                'gender': gender,
                'medications': list(meds),
                'symptoms': list(symptoms)
            })
        
        return pd.DataFrame(data)
    
    @staticmethod
    def prepare_datasets(df, tokenizer, max_length, test_size=0.2):
        """Prepare datasets for training"""
        texts = df['text'].tolist()
        labels = df['disease_category'].tolist()
        
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            texts, labels, test_size=test_size, random_state=42, stratify=labels
        )
        
        train_dataset = PatientDataset(train_texts, train_labels, tokenizer, max_length)
        val_dataset = PatientDataset(val_texts, val_labels, tokenizer, max_length)
        
        return train_dataset, val_dataset

class HealthcarePredictor:
    """Inference class for healthcare predictions"""
    def __init__(self, model_path: str = None):
        self.config = HealthcareLNPConfig()
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        
        self.model = HealthcareLNP(self.config)
        
        if model_path:
            state_dict = torch.load(model_path, map_location=self.config.device)
            self.model.load_state_dict(state_dict)
        
        self.model.to(self.config.device)
        self.model.eval()
    
    def predict(self, medical_text: str):
        """Make predictions on medical text"""
        encoding = self.tokenizer(
            medical_text,
            truncation=True,
            padding='max_length',
            max_length=self.config.max_length,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(self.config.device)
        attention_mask = encoding['attention_mask'].to(self.config.device)
        
        with torch.no_grad():
            outputs = self.model(input_ids, attention_mask)
        
        # Process outputs
        disease_pred = torch.softmax(outputs['disease'], dim=1)
        disease_class = torch.argmax(disease_pred, dim=1).item()
        disease_name = MedicalDataProcessor.DISEASE_CATEGORIES.get(disease_class, "Unknown")
        
        medication_pred = torch.sigmoid(outputs['medication'])
        # Get top 5 medications
        top_meds_idx = torch.topk(medication_pred.flatten(), 5).indices
        suggested_meds = [MedicalDataProcessor.COMMON_MEDICATIONS[int(i)] for i in top_meds_idx.cpu().numpy()]
        
        severity_pred = torch.softmax(outputs['severity'], dim=1)
        severity = ['Mild', 'Moderate', 'Severe'][torch.argmax(severity_pred, dim=1).item()]
        
        risk_score = outputs['risk_score'].item()
        
        return {
            'disease_prediction': disease_name,
            'disease_confidence': disease_pred.max().item(),
            'suggested_medications': suggested_meds,
            'severity_assessment': severity,
            'risk_score': risk_score,
            'symptoms_identified': self.extract_symptoms(outputs['symptoms'])
        }
    
    def extract_symptoms(self, symptom_output):
        """Extract symptoms from model output"""
        threshold = 0.5
        symptom_probs = torch.sigmoid(symptom_output).flatten()
        detected_indices = (symptom_probs > threshold).nonzero().flatten()
        
        # Map to symptom names (simplified)
        symptom_names = [f"Symptom_{i+1}" for i in range(100)]
        return [symptom_names[i] for i in detected_indices.cpu().numpy()][:5]

def main():
    """Main training pipeline"""
    print("Initializing Healthcare LNP Model...")
    
    # Configuration
    config = HealthcareLNPConfig()
    print(f"Using device: {config.device}")
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(config.model_name)
    print("Tokenizer loaded successfully")
    
    # Create sample data
    print("Creating sample medical data...")
    df = MedicalDataProcessor.create_sample_data(num_samples=2000)
    print(f"Created {len(df)} medical records")
    
    # Prepare datasets
    train_dataset, val_dataset = MedicalDataProcessor.prepare_datasets(
        df, tokenizer, config.max_length
    )
    
    train_dataloader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True)
    val_dataloader = DataLoader(val_dataset, batch_size=config.batch_size, shuffle=False)
    
    # Initialize model
    model = HealthcareLNP(config)
    print(f"Model initialized with {sum(p.numel() for p in model.parameters()):,} parameters")
    
    # Train
    trainer = HealthcareAITrainer(model, config, tokenizer)
    print("Starting training...")
    trainer.train(train_dataloader, val_dataloader)
    
    # Save model
    torch.save(model.state_dict(), 'healthcare_lnp_model.pth')
    print("Model saved as 'healthcare_lnp_model.pth'")
    
    # Test inference
    predictor = HealthcarePredictor('healthcare_lnp_model.pth')
    
    test_cases = [
        "65 year old male with chest pain and shortness of breath. History of hypertension and diabetes. BP 150/95, HR 110. Suspected myocardial infarction.",
        "28 year old female with fever, cough, and fatigue for 3 days. Temperature 38.5C. Suspected viral infection.",
        "45 year old male with persistent headache and dizziness. BP 160/100. No significant medical history."
    ]
    
    print("\n\nTesting Inference on Sample Cases:")
    print("=" * 80)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\nCase {i}:")
        print(f"Input: {case[:100]}...")
        result = predictor.predict(case)
        
        print(f"Predicted Disease: {result['disease_prediction']} (Confidence: {result['disease_confidence']:.2%})")
        print(f"Severity: {result['severity_assessment']}")
        print(f"Suggested Medications: {', '.join(result['suggested_medications'][:3])}")
        print(f"Risk Score: {result['risk_score']:.2%}")
    
    return model, predictor

if __name__ == "__main__":
    model, predictor = main()