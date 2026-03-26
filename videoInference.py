import os
import cv2
from ultralytics import YOLO

# ====== CONFIGURATION ======
model_path = r"D:\models_list\rs\6\best.pt"       # Path to your trained model
input_folder = r"D:\RS_Videos\paramount"                  # Folder containing videos
output_folder = r"D:\RS_Videos\paramount\inference"             # Folder to save inferenced videos
conf_threshold = 0.3                                # Confidence threshold
# ============================

# Create output folder if not exists
os.makedirs(output_folder, exist_ok=True)

# Load YOLO model
model = YOLO(model_path)

# Supported video formats
video_extensions = (".mp4", ".avi", ".mov", ".mkv")

# Loop through all videos in folder
for file_name in os.listdir(input_folder):
    if file_name.lower().endswith(video_extensions):
        input_path = os.path.join(input_folder, file_name)
        output_path = os.path.join(output_folder, f"inferenced_{file_name}")

        print(f"Processing: {file_name}")

        cap = cv2.VideoCapture(input_path)

        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Run YOLO inference
            results = model(frame, conf=conf_threshold)

            # Draw detections on frame
            annotated_frame = results[0].plot()

            # Write frame
            out.write(annotated_frame)

        cap.release()
        out.release()

        print(f"Saved: {output_path}")

print("All videos processed successfully.")