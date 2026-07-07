import cv2
import numpy as np
from ultralytics import YOLO
import time

# -----------------------------
# CONFIG
# -----------------------------

RTSP_URL = r"rtsp://admin:paramount123@192.168.0.37:554/Streaming/Channels/101"
MODEL_PATH = r"D:\models_list\rs\6\best.pt"
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720

TARGET_CLASS = "customer"   # change if you want another class

# -----------------------------
# LOAD MODEL
# -----------------------------

model = YOLO(MODEL_PATH)

# -----------------------------
# VIDEO CAPTURE
# -----------------------------

def create_capture():
    cap = cv2.VideoCapture(RTSP_URL)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
    return cap

cap = create_capture()

# -----------------------------
# VARIABLES
# -----------------------------

line_points = []
drawing = False

count = 0
crossed_ids = set()

previous_positions = {}

# -----------------------------
# MOUSE FUNCTION
# -----------------------------

def draw_line(event, x, y, flags, param):
    global line_points, drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        line_points = [(x, y)]
        drawing = True

    elif event == cv2.EVENT_MOUSEMOVE and drawing:

        if len(line_points) == 1:
            line_points.append((x, y))
        else:
            line_points[1] = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False


# -----------------------------
# LINE SIDE FUNCTION
# -----------------------------

def side_of_line(px, py, x1, y1, x2, y2):
    return np.sign((px-x1)*(y2-y1) - (py-y1)*(x2-x1))


# -----------------------------
# WINDOW
# -----------------------------

cv2.namedWindow("Video", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Video", DISPLAY_WIDTH, DISPLAY_HEIGHT)

cv2.setMouseCallback("Video", draw_line)

# -----------------------------
# MAIN LOOP
# -----------------------------

while True:

    ret, frame = cap.read()

    # RTSP reconnect if stream stops
    if not ret:
        print("⚠️ Stream disconnected. Reconnecting...")
        cap.release()
        time.sleep(2)
        cap = create_capture()
        continue

    frame = cv2.resize(frame, (DISPLAY_WIDTH, DISPLAY_HEIGHT))

    results = model.track(frame, persist=True)

    if results[0].boxes.id is not None:

        boxes = results[0].boxes.xyxy.cpu().numpy()
        ids = results[0].boxes.id.cpu().numpy()
        classes = results[0].boxes.cls.cpu().numpy()
        confs = results[0].boxes.conf.cpu().numpy()

        for box, track_id, cls, conf in zip(boxes, ids, classes, confs):

            x1, y1, x2, y2 = map(int, box)

            label = model.names[int(cls)]

            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            # Draw detection box
            cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)

            # Draw label
            text = f"{label} ID:{int(track_id)} {conf:.2f}"

            cv2.putText(frame,
                        text,
                        (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0,255,0),
                        2)

            cv2.circle(frame, (cx,cy), 4, (0,255,0), -1)

            # COUNTING
            if label == TARGET_CLASS:

                if track_id in previous_positions and len(line_points) == 2:

                    prev = previous_positions[track_id]

                    xL1, yL1 = line_points[0]
                    xL2, yL2 = line_points[1]

                    prev_side = side_of_line(prev[0], prev[1], xL1, yL1, xL2, yL2)
                    curr_side = side_of_line(cx, cy, xL1, yL1, xL2, yL2)

                    if prev_side != curr_side and track_id not in crossed_ids:
                        count += 1
                        crossed_ids.add(track_id)

                previous_positions[track_id] = (cx, cy)

    # Draw line
    if len(line_points) == 2:
        cv2.line(frame, line_points[0], line_points[1], (0,0,255), 3)

    # Show count
    cv2.putText(frame,
                f"Count ({TARGET_CLASS}): {count}",
                (20,50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,0,255),
                3)

    cv2.imshow("Video", frame)

    key = cv2.waitKey(1)

    if key == 27:
        break

# -----------------------------
# CLEANUP
# -----------------------------

cap.release()
cv2.destroyAllWindows()