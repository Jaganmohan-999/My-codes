import cv2
import time

# ---------- CONFIG ----------
RTSP_URLS = [
    "rtsp://SIVNJ:sivn%40654321@106.51.53.65:1800/Streaming/Channels/1901"
]

TEST_DURATION = 20  # seconds per stream


# ---------- CHECK STREAM ----------
def check_stream(rtsp_url):
    print(f"\n🎥 Checking: {rtsp_url}")

    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print("❌ Cannot connect to stream")
        return

    start_time = time.time()
    frame_count = 0
    last_frame_time = time.time()
    delays = []
    freeze_count = 0

    while time.time() - start_time < TEST_DURATION:
        ret, frame = cap.read()

        if not ret or frame is None:
            print("⚠️ Frame read failed (possible drop)")
            continue

        frame_count += 1

        current_time = time.time()
        delay = current_time - last_frame_time
        delays.append(delay)

        # Detect freeze (no new frame)
        if delay > 0.5:
            freeze_count += 1

        last_frame_time = current_time

    cap.release()

    # ---------- METRICS ----------
    total_time = time.time() - start_time
    fps = frame_count / total_time if total_time > 0 else 0
    avg_delay = sum(delays) / len(delays) if delays else 0

    print("\n📊 RESULT")
    print(f"Frames Captured: {frame_count}")
    print(f"FPS: {fps:.2f}")
    print(f"Average Frame Delay: {avg_delay:.3f} sec")
    print(f"Freeze Events: {freeze_count}")

    # ---------- QUALITY VERDICT ----------
    if fps >= 20 and freeze_count == 0:
        print("✅ Smooth stream")
    elif fps >= 10:
        print("⚠️ Moderate (some lag)")
    else:
        print("❌ Poor stream (lag / drops)")


# ---------- MAIN ----------
def main():
    for url in RTSP_URLS:
        check_stream(url)


if __name__ == "__main__":
    main()