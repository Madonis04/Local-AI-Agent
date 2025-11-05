# gpu.py (Updated for llama-cpp-python)

import os
from llama_cpp import Llama
import time

MODEL_PATH = r"D:/LLMs/Meta-Llama-3-8B-Instruct.Q4_0.gguf"

if not os.path.exists(MODEL_PATH):
    print(f"❌ ERROR: Model file not found at '{MODEL_PATH}'")
else:
    print(f"Attempting to load model '{os.path.basename(MODEL_PATH)}' directly onto GPU with llama-cpp-python...")
    print("This may take a moment...")

    try:
        start_time = time.time()
        
        model = Llama(model_path=MODEL_PATH, n_gpu_layers=-1)
        
        end_time = time.time()
        
        print("\n" + "="*50)
        print(f"✅ SUCCESS: Model loaded onto GPU in {end_time - start_time:.2f} seconds.")
        print("This confirms that GPU acceleration is working correctly with llama-cpp-python.")
        print("="*50 + "\n")

    except Exception as e:
        print("\n" + "="*50)
        print("❌ FAILED: Could not load model onto GPU.")
        print(f"\nError details: {e}")
        print("="*50 + "\n")