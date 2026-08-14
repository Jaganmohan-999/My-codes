import cv2

# 🔹 Base RTSP URL
base_rtsp = "rtsp://RSDNJEW:rsdn@2026@183.82.99.55:1800/Streaming/Channels/{}"

start_channel = 101
end_channel = 3201
step = 100

rtsp_urls = [
    (ch, base_rtsp.format(ch))
    for ch in range(start_channel, end_channel + 1, step)
]

def check_stream(channel, url, timeout_frames=20):
    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)

    if not cap.isOpened():
        cap.release()
        return False

    for _ in range(timeout_frames):
        ret, frame = cap.read()
        if ret and frame is not None:
            cap.release()
            return True

    cap.release()
    return False


# 🔹 Store working URLs
working_urls = []

# 🔹 Process all channels
for channel, url in rtsp_urls:
    if check_stream(channel, url):
        print(f"✅ Working: {url}")
        working_urls.append(url)
    else:
        print(f"❌ Not Working: {url}")

# 🔹 Final Output
print("\n======= WORKING URLS =======")
for url in working_urls:
    print(url)
