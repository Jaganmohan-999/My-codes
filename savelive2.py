import subprocess
import os
import threading

BASE_RTSP = "rtsp://SIMGJ:mgjew@654321@183.82.114.243:1800/Streaming/Channels/{}"

CHANNELS = [801
]

RECORD_SECONDS = 300
OUTPUT_DIR =r"D:\RS_Videos\Videos"
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
