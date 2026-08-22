import os
import cv2

# ==========================
# CONFIG
# ==========================
INPUT_VIDEO = r"/Users/tp-01/Downloads/WhatsApp Video 2026-08-21 at 7.16.21 PM.mp4"

OUTPUT_IMAGE = r"/Users/tp-01/Downloads/mobile/FIFTHFLOOR-1.jpg"
# ==========================


def capture_snapshot(video_path, output_path):

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("❌ Could not open video.")
        return

    ret = False
    frame = None

    # Read until first valid frame
    for _ in range(30):
        ret, frame = cap.read()

        if ret and frame is not None:
            break

    cap.release()

    if not ret:
        print("❌ Could not read any frame.")
        return

    # Create output folder if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cv2.imwrite(output_path, frame)

    print("✅ Snapshot saved:")
    print(output_path)


if __name__ == "__main__":
    capture_snapshot(INPUT_VIDEO, OUTPUT_IMAGE)