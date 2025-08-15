import torch
import sys

def check_gpu():
    print(f"Python version: {sys.version}")
    print(f"PyTorch version: {torch.__version__}")
    print("-" * 30)
    
    is_available = torch.cuda.is_available()
    print(f"Is CUDA available? {is_available}")
    
    if is_available:
        print(f"CUDA version: {torch.version.cuda}")
        device_count = torch.cuda.device_count()
        print(f"Number of GPUs available: {device_count}")
        for i in range(device_count):
            print(f"--- GPU {i} ---")
            print(f"Name: {torch.cuda.get_device_name(i)}")
            print(f"Compute capability: {torch.cuda.get_device_capability(i)}")
            total_mem = torch.cuda.get_device_properties(i).total_memory / (1024**3)
            print(f"Total memory: {total_mem:.2f} GB")
    else:
        print("CUDA is not available. PyTorch is running on CPU.")
        print("Possible reasons:")
        print("1. NVIDIA drivers are not installed or not up to date.")
        print("2. The installed PyTorch version does not have CUDA support.")
        print("3. The CUDA toolkit version is incompatible with your NVIDIA driver.")

if __name__ == "__main__":
    check_gpu()
