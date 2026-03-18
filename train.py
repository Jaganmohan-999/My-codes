# from ultralytics import YOLO
# import torch

# def main():

#     print("CUDA Available:", torch.cuda.is_available())
#     print("GPU Count:", torch.cuda.device_count())
#     print("Current Device:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")

#     model = YOLO("yolo11x.pt")

#     model.train(
#         data="/mnt/raid1/inference/data.yaml",
#         epochs=120,
#         imgsz=640,
#         batch=6,                 # 🔥 Reduced batch size
#         device=0,
#         workers=8,
#         optimizer="AdamW",
#         lr0=0.0005,
#         cos_lr=True,
#         amp=True,
#         cache=True,
#         patience=20,
#         save_period=20,          # 🔥 Save every 20 epochs
#         project="runs/detect",
#         name="yolo11x_640_batch6",
#         exist_ok=True
#     )

# if __name__ == "__main__":
#     main()



import logging
import os
import sys
from datetime import datetime

import torch
from ultralytics import YOLO


def setup_logging():
    """Configure logging for training"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(
        log_dir,
        f"train_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger("YOLO_Training")


def main():
    logger = setup_logging()

    try:
        logger.info("========== YOLO Training Started ==========")

        # 🔹 GPU Info
        cuda_available = torch.cuda.is_available()
        gpu_count = torch.cuda.device_count()

        logger.info(f"CUDA Available: {cuda_available}")
        logger.info(f"GPU Count: {gpu_count}")

        if cuda_available:
            logger.info(f"Current Device: {torch.cuda.get_device_name(0)}")
            logger.info(f"GPU Memory Total: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        else:
            logger.warning("Running on CPU!")

        # 🔹 Load model
        logger.info("Loading YOLO model: yolo11n.pt")
        model = YOLO("yolo11n.pt")

        logger.info("Starting training...")

        results = model.train(
            data="/mnt/raid1/inference/bndata.yaml",
            epochs=120,
            imgsz=640,
            batch=6,
            device=0,
            workers=8,
            optimizer="AdamW",
            lr0=0.0005,
            cos_lr=True,
            amp=True,
            cache=True,
            patience=20,
            save_period=20,
            project="runs/detect",
            name="yolo11n_640_bnbatch2",
            exist_ok=True
        )

        logger.info("Training completed successfully.")
        logger.info(f"Results saved to: {results.save_dir}")

    except Exception as e:
        logger.exception(f"Training failed: {str(e)}")
        raise

    finally:
        logger.info("========== YOLO Training Finished ==========")


if __name__ == "__main__":
    main()