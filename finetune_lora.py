import subprocess
import sys

if __name__ == "__main__":
    snapshot_download(
       repo_id="Djrango/Qwen2vl-Flux",
       allow_patterns="*.safetensors",      # only the weight files
       local_dir="./models/qwen2vl-flux"
   )

    # Paths (update if your actual paths differ)
    PRETRAINED_MODEL = "./models/qwen2vl-flux"
    IMAGE_FOLDER = "/My_SD_Training/2_images/"
    OUTPUT_FOLDER = "/My_SD_Training/3_output/"
    LOGGING_FOLDER = "/My_SD_Training/4_log/"
    MODEL_OUTPUT_NAME = "satt_fire_v1"

    # Training parameters
    BATCH_SIZE = 1  # Set to 2 if you have enough VRAM
    EPOCHS = 10
    SAVE_EVERY_N_EPOCHS = 1
    PRECISION = "fp16"
    LEARNING_RATE = 1e-4
    LR_SCHEDULER = "cosine_with_restarts"
    LR_WARMUP = 0.10
    LORA_RANK = 64
    LORA_ALPHA = 32
    OPTIMIZER = "adamw8bit"
    LORA_TYPE = "Standard"

    # Path to kohya_ss train_network.py (update if needed)
    KOHYA_TRAIN_SCRIPT = "train_network.py"  # Assumes in PATH or current dir

    # Build the command
    command = [
        sys.executable, KOHYA_TRAIN_SCRIPT,
        "--pretrained_model_name_or_path", PRETRAINED_MODEL,
        "--train_data_dir", IMAGE_FOLDER,
        "--output_dir", OUTPUT_FOLDER,
        "--logging_dir", LOGGING_FOLDER,
        "--output_name", MODEL_OUTPUT_NAME,
        "--resolution", "512,512",
        "--train_batch_size", str(BATCH_SIZE),
        "--max_train_epochs", str(EPOCHS),
        "--save_every_n_epochs", str(SAVE_EVERY_N_EPOCHS),
        "--mixed_precision", PRECISION,
        "--save_precision", PRECISION,
        "--learning_rate", str(LEARNING_RATE),
        "--lr_scheduler", LR_SCHEDULER,
        "--lr_warmup_ratio", str(LR_WARMUP),
        "--network_module", "networks.lora",
        "--network_dim", str(LORA_RANK),
        "--network_alpha", str(LORA_ALPHA),
        "--optimizer_type", OPTIMIZER,
        "--network_train_unet_only",  # LoRA type Standard
    ]

    print("Running kohya_ss LoRA fine-tuning with the following command:")
    print(" ".join(map(str, command)))

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line, end="")
        process.wait()
        if process.returncode == 0:
            print("\nTraining completed successfully.")
        else:
            print(f"\nTraining failed with exit code {process.returncode}.")
    except FileNotFoundError:
        print("Error: kohya_ss train_network.py not found or not executable. Please check your installation and script path.")
    except Exception as e:
        print(f"An error occurred: {e}") 