import cv2

# Replace with your RTSP URL
RTSP_URL = "rtsp://RSKPJ:rskp@2024@183.82.99.76:1810/Streaming/Channels/101"

cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("❌ Error: Unable to open RTSP stream")
    exit()

print("✅ RTSP stream opened successfully")

while True:
    ret, frame = cap.read()

    if not ret:
        print("⚠️ Failed to grab frame")
        break

    cv2.imshow("RTSP Live Stream", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
