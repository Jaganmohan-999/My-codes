import cv2
import os

# ====== SETTINGS ======
image_folder = r"D:\RS_logs\69c64bfabfdb061267dfcc8f"  # folder containing images
output_video = r"D:\RS_logs\69c64bfabfdb061267dfcc8f\output_video.mp4"  # output video file path
fps = 3  # frames per second

# ======================

# Get all image files and sort them
images = [img for img in os.listdir(image_folder) if img.endswith((".png", ".jpg", ".jpeg"))]
images.sort()  # IMPORTANT: ensures correct order

# Read first image to get dimensions
first_image_path = os.path.join(image_folder, images[0])
frame = cv2.imread(first_image_path)
height, width, layers = frame.shape

# Define video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

# Write images to video
for image in images:
    image_path = os.path.join(image_folder, image)
    frame = cv2.imread(image_path)
    video.write(frame)

# Release everything
video.release()
print("✅ Video created successfully!")