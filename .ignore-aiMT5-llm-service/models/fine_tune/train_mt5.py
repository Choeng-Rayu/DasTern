"""
MT5-Small Fine-Tuning Script for OCR Error Correction

Fine-tunes MT5-small on medical prescription OCR error correction.
Supports: English, Khmer, French

Usage:
    python train_mt5.py --data_path ./training_data.json --epochs 3
"""

import os
import json
import argparse
from typing import List, Dict

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    MT5ForConditionalGeneration,
    MT5Tokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorForSeq2Seq
)


class OCRCorrectionDataset(Dataset):
    """Dataset for OCR error correction training."""
    
    def __init__(self, data: List[Dict], tokenizer, max_length: int = 256):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        
        # Input format: "fix_ocr_{lang}: {noisy_text}"
        input_text = f"fix_ocr_{item['lang']}: {item['input']}"
        target_text = item['output']
        
        # Tokenize
        inputs = self.tokenizer(
            input_text,
            max_length=self.max_length,
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        )
        
        targets = self.tokenizer(
            target_text,
            max_length=self.max_length,
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        )
        
        return {
            "input_ids": inputs["input_ids"].squeeze(),
            "attention_mask": inputs["attention_mask"].squeeze(),
            "labels": targets["input_ids"].squeeze()
        }


def load_training_data(file_path: str) -> List[Dict]:
    """
    Load training data from JSON file.
    
    Expected format:
    [
        {"lang": "eng", "input": "paracetamo1 500 mg", "output": "Paracetamol 500mg"},
        {"lang": "khm", "input": "ថ្នាំ បញ្ចុះ កម្ដៅ", "output": "ថ្នាំបញ្ចុះកម្ដៅ"},
        {"lang": "fra", "input": "comprimé 2x par jour", "output": "comprimé 2 fois par jour"}
    ]
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_sample_training_data() -> List[Dict]:
    """Create sample training data for demonstration."""
    return [
        # English samples
        {"lang": "eng", "input": "paracetamo1 500 mg 2 x daY", "output": "Paracetamol 500mg, twice daily"},
        {"lang": "eng", "input": "amoxici11in 250 rng", "output": "Amoxicillin 250mg"},
        {"lang": "eng", "input": "ibupr0fen 400mg 3x daily", "output": "Ibuprofen 400mg, three times daily"},
        {"lang": "eng", "input": "take 1 tab1et after mea1s", "output": "Take 1 tablet after meals"},
        {"lang": "eng", "input": "asprin 100 mg once dai1y", "output": "Aspirin 100mg once daily"},
        
        # Khmer samples
        {"lang": "khm", "input": "ថ្នាំ បញ្ចុះ កម្ដៅ", "output": "ថ្នាំបញ្ចុះកម្ដៅ"},
        {"lang": "khm", "input": "ពីរ គ្រាប់ ម្ដង ក្នុង មួយ ថ្ងៃ", "output": "ពីរគ្រាប់ម្ដងក្នុងមួយថ្ org"},
        
        # French samples
        {"lang": "fra", "input": "comprimé 2x par jour", "output": "comprimé 2 fois par jour"},
        {"lang": "fra", "input": "prendre avant 1es repas", "output": "prendre avant les repas"},
        {"lang": "fra", "input": "une cu1llère à soupe", "output": "une cuillère à soupe"},
    ]


def train(
    data_path: str = None,
    output_dir: str = "../mt5",
    epochs: int = 3,
    batch_size: int = 4,
    learning_rate: float = 5e-5,
    max_length: int = 256
):
    """
    Fine-tune MT5-small on OCR correction data.
    """
    print("Loading MT5-small model and tokenizer...")
    model_name = "google/mt5-small"
    tokenizer = MT5Tokenizer.from_pretrained(model_name)
    model = MT5ForConditionalGeneration.from_pretrained(model_name)
    
    # Load or create training data
    if data_path and os.path.exists(data_path):
        print(f"Loading training data from {data_path}")
        data = load_training_data(data_path)
    else:
        print("Using sample training data (for demonstration)")
        data = create_sample_training_data()
    
    print(f"Training on {len(data)} samples")
    
    # Create dataset
    dataset = OCRCorrectionDataset(data, tokenizer, max_length)
    
    # Training arguments (optimized for CPU)
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        learning_rate=learning_rate,
        warmup_steps=100,
        weight_decay=0.01,
        logging_dir=f"{output_dir}/logs",
        logging_steps=10,
        save_steps=500,
        save_total_limit=2,
        fp16=False,  # CPU training
        dataloader_num_workers=0,
    )
    
    # Data collator
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=data_collator,
    )
    
    print("Starting training...")
    trainer.train()
    
    # Save model and tokenizer
    print(f"Saving model to {output_dir}")
    model.save_pretrained(f"{output_dir}/model")
    tokenizer.save_pretrained(f"{output_dir}/tokenizer")
    
    print("Training complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune MT5-small for OCR correction")
    parser.add_argument("--data_path", type=str, help="Path to training data JSON")
    parser.add_argument("--output_dir", type=str, default="../mt5", help="Output directory")
    parser.add_argument("--epochs", type=int, default=3, help="Number of epochs")
    parser.add_argument("--batch_size", type=int, default=4, help="Batch size")
    parser.add_argument("--lr", type=float, default=5e-5, help="Learning rate")
    
    args = parser.parse_args()
    train(args.data_path, args.output_dir, args.epochs, args.batch_size, args.lr)

