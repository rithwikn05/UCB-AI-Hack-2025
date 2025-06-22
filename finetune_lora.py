#!/usr/bin/env python3

import subprocess
import sys
import os
import time
import torch
from huggingface_hub import snapshot_download

def check_gpu_availability():
    """Check GPU availability and print info"""
    if torch.cuda.is_available():
        gpu_count = torch.cuda.device_count()
        print(f"✓ CUDA available with {gpu_count} GPU(s)")
        for i in range(gpu_count):
            gpu_name = torch.cuda.get_device_name(i)
            gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
            print(f"  GPU {i}: {gpu_name} ({gpu_memory:.1f}GB)")
        return True
    else:
        print("✗ CUDA not available - training will be very slow!")
        return False

def mount_gcs_bucket(bucket_name, mount_point, bucket_path=""):
    """Mount GCS bucket using gcsfuse with optimizations for ML workloads"""
    try:
        os.makedirs(mount_point, exist_ok=True)
        
        # Check if already mounted
        result = subprocess.run(['mountpoint', mount_point], capture_output=True)
        if result.returncode == 0:
            print(f"✓ Bucket already mounted at {mount_point}")
            return os.path.join(mount_point, bucket_path) if bucket_path else mount_point
        
        # Optimized gcsfuse options for ML training
        mount_command = [
            "gcsfuse",
            "--implicit-dirs",
            "--file-mode", "644",
            "--dir-mode", "755",
            "--cache-type", "stat",  # Cache file stats for better performance
            "--stat-cache-ttl", "1h",
            "--type-cache-ttl", "1h",
            "--max-conns-per-host", "10",  # More connections for parallel access
            "--max-idle-conns-per-host", "100",
            bucket_name,
            mount_point
        ]
        
        print(f"🔄 Mounting gs://{bucket_name} to {mount_point}")
        result = subprocess.run(mount_command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Mount successful!")
            full_path = os.path.join(mount_point, bucket_path) if bucket_path else mount_point
            
            # Verify the path exists and has files
            if os.path.exists(full_path):
                file_count = len([f for f in os.listdir(full_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
                print(f"✓ Found {file_count} image files in {full_path}")
                return full_path
            else:
                print(f"⚠️  Path {full_path} not found, using mount root")
                return mount_point
        else:
            print(f"✗ Mount failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"✗ Error mounting GCS bucket: {e}")
        return None

def unmount_gcs_bucket(mount_point):
    """Unmount GCS bucket"""
    try:
        print(f"🔄 Unmounting {mount_point}")
        result = subprocess.run(["fusermount", "-u", mount_point], capture_output=True)
        if result.returncode != 0:
            subprocess.run(["umount", mount_point], capture_output=True)
        print("✓ Unmount completed")
    except Exception as e:
        print(f"⚠️  Unmount error: {e}")

def optimize_training_params(gpu_count, gpu_memory_gb):
    """Optimize training parameters based on available GPU resources"""
    if gpu_memory_gb >= 24:  # RTX 4090, A100, etc.
        return {
            'batch_size': 4 if gpu_count >= 2 else 2,
            'resolution': '1024,1024',
            'precision': 'bf16',
            'gradient_checkpointing': False
        }
    elif gpu_memory_gb >= 16:  # RTX 4080, etc.
        return {
            'batch_size': 2,
            'resolution': '768,768',
            'precision': 'fp16',
            'gradient_checkpointing': True
        }
    elif gpu_memory_gb >= 12:  # RTX 4070 Ti, etc.
        return {
            'batch_size': 1,
            'resolution': '512,512',
            'precision': 'fp16',
            'gradient_checkpointing': True
        }
    else:  # Lower memory GPUs
        return {
            'batch_size': 1,
            'resolution': '512,512',
            'precision': 'fp16',
            'gradient_checkpointing': True
        }

if __name__ == "__main__":
    print("🚀 Starting LoRA Training Setup")
    
    # Check GPU availability
    has_gpu = check_gpu_availability()
    if not has_gpu:
        response = input("No GPU detected. Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Configuration
    GCS_BUCKET_NAME = "processed_tif_images"  # Replace with your bucket
    GCS_BUCKET_PATH = "test_images"  # Replace with your path
    MOUNT_POINT = "/tmp/gcs_training_data"
    
    # Get GPU info for optimization
    gpu_memory_gb = 0
    gpu_count = 0
    if has_gpu:
        gpu_count = torch.cuda.device_count()
        gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
    
    # Optimize parameters based on hardware
    params = optimize_training_params(gpu_count, gpu_memory_gb)
    print(f"📊 Optimized settings: {params}")
    
    mounted_path = None
    try:
        # Download model weights
        print("📥 Downloading model weights...")
        snapshot_download(
            repo_id="Djrango/Qwen2vl-Flux",
            allow_patterns="*.safetensors",
            local_dir="./models/qwen2vl-flux"
        )
        
        # Mount GCS bucket
        # mounted_path = mount_gcs_bucket(GCS_BUCKET_NAME, MOUNT_POINT, GCS_BUCKET_PATH)
        # if not mounted_path:
        #     print("✗ Failed to mount GCS bucket")
        #     sys.exit(1)
        
        # Paths
        PRETRAINED_MODEL = "./models/qwen2vl-flux"
        IMAGE_FOLDER = "/test_images"
        #mounted_path
        OUTPUT_FOLDER = "./output"
        LOGGING_FOLDER = "./logs"
        MODEL_OUTPUT_NAME = "earthly_echoes"
        
        # Create output directories
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        os.makedirs(LOGGING_FOLDER, exist_ok=True)
        
        # Training parameters (optimized for GPU)
        EPOCHS = 10
        SAVE_EVERY_N_EPOCHS = 1
        LEARNING_RATE = 1e-4
        LR_SCHEDULER = "cosine_with_restarts"
        LR_WARMUP = 0.10
        LORA_RANK = 64
        LORA_ALPHA = 32
        OPTIMIZER = "adamw8bit"
        
        # Build command
        command = [
            sys.executable, "train_network.py",
            "--pretrained_model_name_or_path", PRETRAINED_MODEL,
            "--train_data_dir", IMAGE_FOLDER,
            "--output_dir", OUTPUT_FOLDER,
            "--logging_dir", LOGGING_FOLDER,
            "--output_name", MODEL_OUTPUT_NAME,
            "--resolution", params['resolution'],
            "--train_batch_size", str(params['batch_size']),
            "--max_train_epochs", str(EPOCHS),
            "--save_every_n_epochs", str(SAVE_EVERY_N_EPOCHS),
            "--mixed_precision", params['precision'],
            "--save_precision", params['precision'],
            "--learning_rate", str(LEARNING_RATE),
            "--lr_scheduler", LR_SCHEDULER,
            "--lr_warmup_ratio", str(LR_WARMUP),
            "--network_module", "networks.lora",
            "--network_dim", str(LORA_RANK),
            "--network_alpha", str(LORA_ALPHA),
            "--optimizer_type", OPTIMIZER,
            "--network_train_unet_only",
        ]
        
        # Add GPU-specific optimizations
        if has_gpu:
            if params['gradient_checkpointing']:
                command.append("--gradient_checkpointing")
            if gpu_count > 1:
                command.extend(["--multi_gpu", "--num_processes", str(gpu_count)])
        
        print("🏋️  Starting LoRA training with command:")
        print(" ".join(command))
        print("=" * 80)
        
        # Run training
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        for line in process.stdout:
            print(line, end="")
        
        process.wait()
        
        if process.returncode == 0:
            print("\n🎉 Training completed successfully!")
            print(f"📁 Model saved to: {OUTPUT_FOLDER}")
        else:
            print(f"\n💥 Training failed with exit code {process.returncode}")
            
    except KeyboardInterrupt:
        print("\n⏹️  Training interrupted by user")
        if 'process' in locals():
            process.terminate()
    except Exception as e:
        print(f"\n💥 Error during training: {e}")
    finally:
        # Cleanup
        # if mounted_path:
        #     unmount_gcs_bucket(MOUNT_POINT)
        print("🧹 Cleanup completed")