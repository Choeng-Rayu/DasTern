import torch
import psutil
import os

def check_resources(model_name="mT5-Base"):
    # Theoretical weights size in GB (Approximate)
    # mT5-Small: ~300M params * 4 bytes (FP32) ≈ 1.2 GB
    # mT5-Base:  ~580M params * 4 bytes (FP32) ≈ 2.3 GB
    requirements = {
        "mt5-small": {"ram": 4.0, "vram": 2.0},
        "mt5-base": {"ram": 8.0, "vram": 4.0}
    }
    
    key = model_name.lower()
    req = requirements.get(key, requirements["mt5-base"])
    
    print(f"--- Checking Requirements for {model_name} ---")
    
    # 1. Check System RAM
    total_ram = psutil.virtual_memory().total / (1024**3)
    available_ram = psutil.virtual_memory().available / (1024**3)
    print(f"System RAM: {available_ram:.2f} GB available (out of {total_ram:.2f} GB)")
    
    if available_ram < req["ram"]:
        print(f"⚠️ Warning: RAM might be tight. Recommended: {req['ram']} GB")
    else:
        print("✅ RAM: Sufficient")

    # 2. Check GPU VRAM
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        total_vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        # Note: torch.cuda.memory_reserved only shows what Torch is using, 
        # so we assume total capacity for this check.
        print(f"GPU: {gpu_name}")
        print(f"VRAM: {total_vram:.2f} GB total")
        
        if total_vram < req["vram"]:
            print(f"⚠️ Warning: VRAM is below recommended {req['vram']} GB. Consider using CPU or 8-bit quantization.")
        else:
            print("✅ GPU VRAM: Sufficient")
    else:
        print("ℹ️ No NVIDIA GPU detected. You will need to run on CPU.")
        if available_ram < (req["ram"] + 2): # Extra buffer for CPU inference
            print("⚠️ Warning: Running on CPU requires extra System RAM buffer.")

# Check for mT5-Base
check_resources("mt5-base")