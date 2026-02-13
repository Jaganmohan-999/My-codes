import os
import time
from confluent_kafka import Consumer

frame_count = 0
start_time = time.time()
 
# ================= CONFIG =================
KAFKA_BROKER = "91.203.133.191"
TOPIC = r"^frames\..*"
GROUP_ID = "file-saver"
OUTPUT_DIR = "received_frames"
FILE_EXT = ".jpg"   # change if needed
# ==========================================
 
os.makedirs(OUTPUT_DIR, exist_ok=True)
 
conf = {
    "bootstrap.servers": KAFKA_BROKER,
    "group.id": GROUP_ID,
    "auto.offset.reset": "latest",
    "enable.auto.commit": True,
}
 
consumer = Consumer(conf)
consumer.subscribe([TOPIC])
 
print(f"📥 Listening on topic: {TOPIC}")
print(f"📂 Saving files to: {OUTPUT_DIR}")
 
try:
    while True:
        msg = consumer.poll(1.0)
 
        if msg is None:
            continue
 
        if msg.error():
            print("❌ Kafka error:", msg.error())
            continue
 
        data = msg.value()
        timestamp = int(time.time() * 1000)
        filename = f"{OUTPUT_DIR}/frame_{timestamp}_{msg.offset()}{FILE_EXT}"
 
        with open(filename, "wb") as f:
            f.write(data)

        frame_count += 1

        current_time = time.time()
        elapsed = current_time - start_time

        if elapsed >= 1.0:
            fps = frame_count / elapsed
            print(f"📊 FPS: {fps:.2f} frames/sec (last {elapsed:.2f}s)")
            frame_count = 0
            start_time = current_time
 
except KeyboardInterrupt:
    print("\n🛑 Consumer stopped")
 
finally:
    consumer.close()