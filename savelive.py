import cv2
import time
import os
import threading

# Base RTSP URL
BASE_RTSP = "rtsp://RSCNJ:rscn%402024@183.82.99.77:1810/Streaming/Channels/{}"

# Channel list
CHANNELS = [101,
1101,
1201
]

# Recording duration (5 minutes)
RECORD_SECONDS = 120

# Output folder
OUTPUT_DIR = r"D:\RS_Videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def record_stream(channel):
    rtsp_url = BASE_RTSP.format(channel)
    output_file = os.path.join(OUTPUT_DIR, f"cam{channel}.mp4")

    print(f"[INFO] Connecting to cam{channel}...")

    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print(f"[ERROR] Cannot open stream cam{channel}")
        return

    # Get stream properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 25  # fallback if camera doesn't provide FPS

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    start_time = time.time()

    print(f"[INFO] Recording cam{channel}...")

    while time.time() - start_time < RECORD_SECONDS:
        ret, frame = cap.read()
        if not ret:
            print(f"[WARNING] Frame read failed for cam{channel}")
            break

        out.write(frame)

    cap.release()
    out.release()

    print(f"[INFO] Finished recording cam{channel}")


# Record all channels in parallel
threads = []

for ch in CHANNELS:
    t = threading.Thread(target=record_stream, args=(ch,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("✅ All recordings completed.")
