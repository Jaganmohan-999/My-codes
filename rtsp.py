import cv2
import os

# 🔹 Base RTSP URL
base_rtsp = "rtsp://SIRMJ:sirm@654321@106.51.5.131:10081/Streaming/Channels/{}"

start_channel = 101
end_channel = 3201
step = 100

# 🔹 Output folder
output_dir = r"D:\RS_frames\SI Rajahmundry"
os.makedirs(output_dir, exist_ok=True)

rtsp_urls = [
    (ch, base_rtsp.format(ch))
    for ch in range(start_channel, end_channel + 1, step)
]

def check_and_save_frame(channel, url, timeout_frames=20):
    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)

    if not cap.isOpened():
        cap.release()
        return False, "Cannot open stream"

    for _ in range(timeout_frames):
        ret, frame = cap.read()
        if ret and frame is not None:
            file_path = os.path.join(output_dir, f"{channel}.jpg")
            cv2.imwrite(file_path, frame)
            cap.release()
            return True, f"Frame saved: {file_path}"

    cap.release()
    return False, "No frames received"

# 🔹 Process all channels
for channel, url in rtsp_urls:
    status, msg = check_and_save_frame(channel, url)
    print(f"{url} -> {'✅' if status else '❌'} {msg}")
