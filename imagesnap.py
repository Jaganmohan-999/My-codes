import os
import json
import cv2

# Path to JSON file
json_file = r"D:\RS_json\SI_Kothapet.json"

# Output folder
output_folder = r"D:\RS_frames\New folder"
os.makedirs(output_folder, exist_ok=True)

# Load JSON list
with open(json_file, "r") as f:
    cameras = json.load(f)

for cam in cameras:
    rtsp_url = cam.get("rtspUrl")
    camera_number = cam.get("cameraNumber")

    if not rtsp_url or not camera_number:
        print(f"Skipping invalid entry: {cam}")
        continue

    print(f"Connecting to camera {camera_number}...")

    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print(f"Failed to connect: {camera_number}")
        continue

    ret, frame = cap.read()

    if ret:
        output_path = os.path.join(output_folder, f"{camera_number}.jpg")
        cv2.imwrite(output_path, frame)
        print(f"Saved snapshot: {output_path}")
    else:
        print(f"Failed to capture frame: {camera_number}")

    cap.release()