import os
import json
import csv
import cv2
from urllib.parse import urlparse

# -------- SETTINGS --------
input_file = r"C:\Users\phani\Desktop\footfall.txt"  # change to .json / .csv / .txt
output_folder = r"D:\RTSP_Snapshots/RS_ALL"  # folder to save snapshots
os.makedirs(output_folder, exist_ok=True)


# -------- FUNCTION: Extract RTSP URLs --------
def load_rtsp_urls(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    urls = []

    if ext == ".json":
        with open(file_path, "r") as f:
            data = json.load(f)
            for item in data:
                if isinstance(item, dict):
                    url = item.get("rtspUrl") or item.get("url")
                    if url:
                        urls.append(url)

    elif ext == ".csv":
        with open(file_path, newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                for col in row:
                    if col.startswith("rtsp://"):
                        urls.append(col)

    elif ext == ".txt":
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("rtsp://"):
                    urls.append(line)

    return urls


# -------- FUNCTION: Parse RTSP URL --------
def parse_rtsp(rtsp_url):
    try:
        parsed = urlparse(rtsp_url)

        # username
        username = parsed.username or "user"

        # port
        port = parsed.port or "554"

        # channel (last number in path or query)
        path = parsed.path
        channel = "ch"

        # try extracting number from path
        parts = path.split("/")
        for p in reversed(parts):
            if p.isdigit():
                channel = p
                break

        return f"{username}_{port}_{channel}"

    except:
        return "unknown_name"


# -------- MAIN --------
rtsp_urls = load_rtsp_urls(input_file)

for rtsp_url in rtsp_urls:
    print(f"Connecting: {rtsp_url}")

    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print("Failed to connect")
        continue

    ret, frame = cap.read()

    if ret:
        filename = parse_rtsp(rtsp_url) + ".jpg"
        output_path = os.path.join(output_folder, filename)

        cv2.imwrite(output_path, frame)
        print(f"Saved: {output_path}")
    else:
        print("Failed to capture frame")

    cap.release()

print("Done!")