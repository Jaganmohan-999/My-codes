from confluent_kafka import Consumer, KafkaException, KafkaError
import logging
import json
import base64
import os
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
KAFKA_BROKER = '13.201.82.150:9092'
TOPIC = 'frames.raw'
GROUP_ID = 'image-consumer-final-v1'

# 👉 Put your camera_id OR set None to disable filtering
TARGET_CAMERA_ID = None
# TARGET_CAMERA_ID = None   # ← use this to debug (no filter)

OUTPUT_DIR = r"D:\RS_Vidx`eos\New folder"
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

# Reduce Kafka internal logs
logging.getLogger('confluent_kafka').setLevel(logging.ERROR)

# -----------------------------
# KAFKA CONFIG
# -----------------------------
conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': GROUP_ID,
    'auto.offset.reset': 'latest',   # only new data
    'enable.auto.commit': True
}

consumer = Consumer(conf)
consumer.subscribe([TOPIC])

print(f"🚀 Listening to topic: {TOPIC}...\n")

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

        # -----------------------------
        # DEBUG (important)
        # -----------------------------
        print("📩 Message received")

        camera_id = data_json.get("camera_id")
        print(f"📷 Camera ID: {camera_id}")

        # -----------------------------
        # FILTER (optional)
        # -----------------------------
        if TARGET_CAMERA_ID and camera_id != TARGET_CAMERA_ID:
            continue

        # -----------------------------
        # GET IMAGE
        # -----------------------------
        base64_img = data_json.get("data")

        if not base64_img:
            print("⚠️ No image data found")
            continue

        try:
            # Handle possible prefix
            if "," in base64_img:
                base64_img = base64_img.split(",")[1]

            img_bytes = base64.b64decode(base64_img)

            # Save image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            frame_id = data_json.get("frame_id", "noid")

            filename = f"{OUTPUT_DIR}/{camera_id}_{frame_id}_{timestamp}.jpg"

            with open(filename, "wb") as f:
                f.write(img_bytes)

            print(f"✅ Image saved: {filename}")

        except Exception as e:
            print(f"❌ Image decode error: {e}")
            logger.error(f"Image decode failed: {e}")

except KeyboardInterrupt:
    print("\n🛑 Stopping consumer...")

finally:
    consumer.close()