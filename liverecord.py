import subprocess
import os
import threading

BASE_RTSP = "rtsp://RSAPJ:rsap@5202@183.82.99.146:1810/Streaming/Channels/{}"

CHANNELS = [101, 201, 302, 401]

RECORD_SECONDS = 300  # 5 minutes

OUTPUT_DIR = r"D:\RS_Videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def record_stream(channel):
    rtsp_url = BASE_RTSP.format(channel)
    output_file = os.path.join(OUTPUT_DIR, f"cam{channel}.mp4")

    print(f"[INFO] Recording cam{channel}...")

    command = [
        "ffmpeg",
        "-rtsp_transport", "tcp",
        "-i", rtsp_url,
        "-t", str(RECORD_SECONDS),
        "-c:v", "copy",
        "-an",
        "-y",
        output_file
    ]

    subprocess.run(command)

    print(f"[INFO] Finished cam{channel}")


threads = []

for ch in CHANNELS:
    t = threading.Thread(target=record_stream, args=(ch,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("\n✅ Recording Summary:\n")

for ch in CHANNELS:
    url = BASE_RTSP.format(ch)
    print(f"{url}")
