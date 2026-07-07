from confluent_kafka import Consumer, KafkaError
import logging
import json
import base64
import os
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
KAFKA_BROKER = '164.52.193.23:9092'
TOPIC = 'frames.raw'

# 🔥 IMPORTANT: new group id for replay
GROUP_ID = 'image-consumer-replay-v1'

# 👉 Camera filter (optional)
TARGET_CAMERA_ID = None
# TARGET_CAMERA_ID = None  # disable if needed

# 👉 Frame IDs from your logs
TARGET_FRAME_IDS = {
   "69a96df392503e9158a176ad"
}

OUTPUT_DIR = r"D:\RS_Videos\New folder2"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------
# LOGGING
# -----------------------------
logging.basicConfig(
    filename="kafka_consumer.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)
logging.getLogger('confluent_kafka').setLevel(logging.ERROR)

# -----------------------------
# KAFKA CONFIG
# -----------------------------
conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': GROUP_ID,
    'auto.offset.reset': 'earliest',   # 🔥 replay old messages
    'enable.auto.commit': True
}

consumer = Consumer(conf)
consumer.subscribe([TOPIC])

print(f"🚀 Listening to topic: {TOPIC} (replay mode)...\n")

# Track downloaded frames (avoid duplicates)
downloaded_frames = set()

# -----------------------------
# MAIN LOOP
# -----------------------------
try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"❌ Kafka Error: {msg.error()}")
                continue

        try:
            value = msg.value().decode('utf-8', errors='ignore')
            data_json = json.loads(value)
        except Exception as e:
            logger.error(f"JSON decode failed: {e}")
            continue

        print("📩 Message received")

        camera_id = data_json.get("camera_id")
        frame_id = data_json.get("frame_id")

        print(f"📷 Camera ID: {camera_id}")
        print(f"🎯 Frame ID: {frame_id}")

        # -----------------------------
        # FILTER: CAMERA
        # -----------------------------
        if TARGET_CAMERA_ID and camera_id != TARGET_CAMERA_ID:
            continue

        # -----------------------------
        # FILTER: FRAME ID
        # -----------------------------
        if TARGET_FRAME_IDS and frame_id not in TARGET_FRAME_IDS:
            continue

        # Avoid duplicate downloads
        if frame_id in downloaded_frames:
            continue

        # -----------------------------
        # GET IMAGE
        # -----------------------------
        base64_img = data_json.get("data")

        if not base64_img:
            print("⚠️ No image data found")
            continue

        try:
            # Handle base64 prefix
            if "," in base64_img:
                base64_img = base64_img.split(",")[1]

            img_bytes = base64.b64decode(base64_img)

            # Save image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{OUTPUT_DIR}/{camera_id}_{frame_id}_{timestamp}.jpg"

            with open(filename, "wb") as f:
                f.write(img_bytes)

            downloaded_frames.add(frame_id)

            print(f"✅ Image saved: {filename}")

            # Optional: stop when all frames downloaded
            if len(downloaded_frames) == len(TARGET_FRAME_IDS):
                print("\n🎉 All target frames downloaded. Exiting...")
                break

        except Exception as e:
            print(f"❌ Image decode error: {e}")
            logger.error(f"Image decode failed: {e}")

except KeyboardInterrupt:
    print("\n🛑 Stopping consumer...")

finally:
    consumer.close()