import os
import cv2
from ultralytics import YOLO

# ====== CONFIGURATION ======
model_path = r"D:\models_list\rs\6\best.pt"       # Path to your trained model
input_folder = r"D:\RS_Videos\input"           # Folder containing images
output_folder = r"D:\RS_Videos\input\out"    # Folder to save inferenced images
conf_threshold = 0.25                             # Confidence threshold
# ============================

# Create output folder if not exists
os.makedirs(output_folder, exist_ok=True)

# Load YOLO model
model = YOLO(model_path)

# Supported image formats
image_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")

# Loop through all images in folder
for file_name in os.listdir(input_folder):
    if file_name.lower().endswith(image_extensions):

        input_path = os.path.join(input_folder, file_name)
        output_path = os.path.join(output_folder, f"inferenced_{file_name}")

        print(f"Processing: {file_name}")

        # Read image
        image = cv2.imread(input_path)

        # Run YOLO inference
        results = model(image, conf=conf_threshold)

        # Draw detections
        annotated_image = results[0].plot()

        # Save image
        cv2.imwrite(output_path, annotated_image)

        print(f"Saved: {output_path}")

print("All images processed successfully.")