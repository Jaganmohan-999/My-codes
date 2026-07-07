import cv2
import subprocess
import os
import time
from datetime import datetime

# ================= CONFIG =================
rtsp_url = "rtsp://admin:paramount123@192.168.0.38:554/Streaming/Channels/101"  # Change to your RTSP URL
OUTPUT_FOLDER = r"/Users/tp-01/Documents/Record_Mobile"
RECORD_SECONDS = 600
# ==========================================

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("Error: Cannot open RTSP stream")
    exit()

cv2.namedWindow("RTSP Live", cv2.WINDOW_NORMAL)

recording = False
process = None
record_start_time = None

print("\nControls:")
print("r → Start Recording")
print("s → Stop Recording")
print("q → Quit\n")

while True:

    ret, frame = cap.read()
    if not ret:
        print("Stream disconnected")
        break

    cv2.imshow("RTSP Live", frame)

    key = cv2.waitKey(1) & 0xFF

    # START RECORDING
    if key == ord('r') and not recording:

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(OUTPUT_FOLDER, f"record_{timestamp}.mp4")

        command = [
            "ffmpeg",
            "-rtsp_transport", "tcp",
            "-i", rtsp_url,
            "-c:v", "copy",
            "-an",
            "-y",
            output_file
        ]

        process = subprocess.Popen(command, stdin=subprocess.PIPE)

        recording = True
        record_start_time = time.time()

        print("Recording started:", output_file)

    # STOP RECORDING MANUALLY
    elif key == ord('s') and recording:

        process.communicate(input=b"q")

        recording = False
        print("Recording stopped")

    # AUTO STOP AFTER MAX TIME
    if recording:
        elapsed = time.time() - record_start_time

        if elapsed >= RECORD_SECONDS:
            print("Max recording time reached")

            process.communicate(input=b"q")

            recording = False

    # QUIT LIVE
    if key == ord('q'):

        if recording:
            print("Stopping recording before exit")
            process.communicate(input=b"q")

        print("Exiting...")
        break


cap.release()
cv2.destroyAllWindows()