import json
import cv2
import time
import os
import numpy as np
from confluent_kafka import Consumer
import logging
import base64

# -------------------------
# LOGGING
# -------------------------
LOG_DIR = "/logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "frames_to_video.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(processName)s] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

log = logging.getLogger(__name__)

# -------------------------
# CONFIG
# -------------------------
KAFKA_BROKER = "164.52.193.23:9092"
TOPIC = "frames.raw"
GROUP_ID = "debug-frames-group"

OUTPUT_DIR = "/opt/triton/assets/raw_videos"
FPS = 5

MAX_VIDEO_SECONDS = 120          # 5 minutes
MAX_VIDEOS_PER_CAMERA = 10       # retention per camera

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------
# Kafka Consumer
# -------------------------
consumer = Consumer({
    "bootstrap.servers": KAFKA_BROKER,
    "group.id": GROUP_ID,
    "auto.offset.reset": "latest",
    "enable.auto.commit": False
})

consumer.subscribe([TOPIC])

# -------------------------
# Video Writers (per camera)
# -------------------------
# camera_id -> {
#   "writer": cv2.VideoWriter,
#   "start": float,
#   "files": [str, ...]
# }
writers = {}


# -------------------------
# Helpers
# -------------------------
def get_camera_dir(camera_id):
    cam_dir = os.path.join(OUTPUT_DIR, camera_id)
    os.makedirs(cam_dir, exist_ok=True)
    return cam_dir


def prune_old_videos(camera_id):
    files = writers[camera_id]["files"]

    while len(files) > MAX_VIDEOS_PER_CAMERA:
        old = files.pop(0)
        try:
            os.remove(old)
            log.info(f"Deleted old video: {old}")
        except FileNotFoundError:
            pass


def get_writer(camera_id, frame_shape, fps):
    now = time.time()

    # Reuse existing writer if still within time limit
    if camera_id in writers:
        elapsed = now - writers[camera_id]["start"]
        if elapsed < MAX_VIDEO_SECONDS:
            return writers[camera_id]["writer"]

        # Rotate video
        log.info(f"Rotating video for {camera_id} after {elapsed:.1f}s")
        writers[camera_id]["writer"].release()

    h, w = frame_shape[:2]
    ts = time.strftime("%Y%m%d_%H%M%S")

    cam_dir = get_camera_dir(camera_id)
    path = os.path.join(cam_dir, f"{camera_id}_{ts}.mp4")

    writer = cv2.VideoWriter(
        path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (w, h)
    )

    if camera_id not in writers:
        writers[camera_id] = {
            "writer": writer,
            "start": now,
            "files": []
        }
    else:
        writers[camera_id]["writer"] = writer
        writers[camera_id]["start"] = now

    writers[camera_id]["files"].append(path)
    prune_old_videos(camera_id)

    log.info(f"Writing debug video: {path}, {w}x{h}")
    return writer

# -------------------------
# Draw detections
# -------------------------
def draw_detections(img, detections):
    h_img, w_img = img.shape[:2]
    log.info(f"draw_detections called, detections={len(detections)}")

    for det in detections:
        if "bbox" not in det:
            log.info("bbox not found")
            continue

        # if det.get("class_name") != "person":
        #     continue

        x1, y1, x2, y2 = det["bbox"]
        label = f"{det.get('class_name')} {det.get('confidence', 0):.2f}"

        # Clamp bbox to image bounds
        x1 = max(0, min(int(x1), w_img - 1))
        y1 = max(0, min(int(y1), h_img - 1))
        x2 = max(0, min(int(x2), w_img - 1))
        y2 = max(0, min(int(y2), h_img - 1))

        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(
            img,
            label,
            (x1, max(y1 - 10, 0)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

    return img

# -------------------------
# Main Loop
# -------------------------
try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            log.info("message not found")
            continue

        if msg.error():
            log.error(f"Kafka error: {msg.error()}")
            continue

        payload = json.loads(msg.value())

        if "data" not in payload:
            log.info("frame data not found in payload")
            continue

        camera_id = payload.get("camera_id", "unknown")
        # detections = payload.get("detections", [])
        if camera_id != "69a96df392503e9158a176ad":
            log.info("camera id not matched to 69a96df392503e9158a176ad")
            continue

        try:
            # Decode JPEG
            # raw = base64.b64decode(payload["frame_jpeg"])
            # # jpeg_bytes = bytes.fromhex(payload["frame_jpeg"])
            # frame = cv2.imdecode(
            #     np.frombuffer(raw, np.uint8),
            #     cv2.IMREAD_COLOR
            # )
            # raw = base64.b64decode(payload["data"])
            # arr = np.frombuffer(raw, dtype=np.uint8).copy()
            # # jpeg = TurboJPEG()
            # # img = jpeg.decode(arr)
            # frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)

            # log.info(f"processing frame detections: {detections}")

            raw = base64.b64decode(payload["data"])
            arr = np.frombuffer(raw, dtype=np.uint8).copy()
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)  # returns BGR natively — correct for preprocess_yolo
            if frame is None:
                raise ValueError(f"cv2.imdecode failed | camera={payload.get('camera_id')}")

        except Exception as e:
            log.error(f"Image reading failed: {str(e)}")
            continue

        # if frame is None:
        #     log.info("frame is None")
        #     continue

        # Draw detections
        # vis = draw_detections(frame, detections)

        fps = payload.get("fps") or FPS
        log.info(f"fps={fps}")

        writer = get_writer(camera_id, frame.shape, fps)
        writer.write(frame)

        # if detections:
        #     log.info(
        #         f"{camera_id}: {len(detections)} detections, "
        #         f"first={detections[0]['bbox']}"
        #     )

        consumer.commit(msg)

except KeyboardInterrupt:
    log.info("Shutting down")

finally:
    for meta in writers.values():
        meta["writer"].release()
    consumer.close()