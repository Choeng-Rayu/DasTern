# setup.py
import subprocess
import sys

def install_requirements():
    requirements = [
        'torch>=2.0.0',
        'transformers>=4.30.0',
        'pandas>=2.0.0',
        'scikit-learn>=1.3.0',
        'numpy>=1.24.0',
        'datasets>=2.13.0',
        'streamlit>=1.25.0',
        'sentence-transformers>=2.2.0',
        'accelerate>=0.21.0'
    ]
    
    for package in requirements:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
    
    print("All requirements installed successfully!")

if __name__ == "__main__":
    install_requirements()