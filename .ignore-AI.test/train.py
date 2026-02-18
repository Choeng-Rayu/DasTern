# train.py
import argparse
from healthcare_lnp import main as train_main

def parse_args():
    parser = argparse.ArgumentParser(description="Train Healthcare LNP Model")
    parser.add_argument('--data_path', type=str, help='Path to custom medical data CSV')
    parser.add_argument('--epochs', type=int, default=10, help='Number of training epochs')
    parser.add_argument('--batch_size', type=int, default=16, help='Batch size')
    parser.add_argument('--learning_rate', type=float, default=2e-5, help='Learning rate')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    train_main()