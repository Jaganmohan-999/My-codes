#!/usr/bin/env python3
"""
Debug Consumer Script
---------------------
Connects to Kafka, consumes frames from 'frames.raw', and saves them to disk.
Performs basic JPEG structure validation to check for corruption.
"""
 
import json
import base64
import os
import time
import sys
 
# Try importing confluent_kafka
try:
    from confluent_kafka import Consumer, KafkaError
except ImportError:
    print("Error: confluent_kafka is not installed.")
    print("Run: pip install confluent-kafka")
    sys.exit(1)
 
# Settings matching your main.py
KAFKA_BROKERS = "164.52.193.23:9092"
KAFKA_TOPIC = "frames.raw"
# Use a dynamic group ID to always get latest messages (don't resume old offsets)
GROUP_ID = "debug-viewer-" + str(int(time.time()))
OUTPUT_DIR = r"D:\kafka\received_frames"
 
def is_valid_jpeg(data: bytes) -> bool:
    """
    Simple check for JPEG SOI (FF D8) and EOI (FF D9) markers.
    """
    if len(data) < 2:
        return False
    # Check header (Start of Image)
    if not data.startswith(b'\xff\xd8'):
        return False
   
    # Check footer (End of Image) - scan last few bytes in case of padding
    # FF D9 is the EOI marker
    if b'\xff\xd9' in data[-10:]:
        return True
       
    return False
 
def main():
    # Ensure output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")
 
    conf = {
        'bootstrap.servers': KAFKA_BROKERS,
        'group.id': GROUP_ID,
        'auto.offset.reset': 'latest',
        'enable.auto.commit': True
    }
 
    try:
        consumer = Consumer(conf)
        consumer.subscribe([KAFKA_TOPIC])
    except Exception as e:
        print(f"❌ Failed to connect to Kafka: {e}")
        return
 
    print(f"✅ Connected to Kafka: {KAFKA_BROKERS}")
    print(f"👀 Watching topic: {KAFKA_TOPIC}")
    print(f"📂 Saving images to: {os.path.abspath(OUTPUT_DIR)}")
    print("Press Ctrl+C to stop...")
 
    count = 0
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
                # 1. Decode JSON
                value_str = msg.value().decode('utf-8')
                payload = json.loads(value_str)
               
                # 2. Extract Data
                metadata = payload.get("metadata", {})
                b64_data = payload.get("jpeg_bytes_b64")
                print(f"metadata: {metadata}")
                frame_id = metadata.get("frame_id", "unknown")
                cam_id = metadata.get("camera_id", "unknown")
                ts = metadata.get("frame_timestamp_ms", int(time.time()*1000))
               
                # 3. Decode Image
                if b64_data:
                    img_bytes = base64.b64decode(b64_data)
                    file_size = len(img_bytes)
                   
                    # 4. Validate Integrity
                    valid = is_valid_jpeg(img_bytes)
                    valid_msg = "✅ Valid JPEG" if valid else "⚠️ POTENTIALLY CORRUPT (Missing EOI)"
                   
                    # 5. Save to Disk
                    filename = f"{cam_id}_{ts}_{frame_id[:8]}.jpg"
                    filepath = os.path.join(OUTPUT_DIR, filename)
                   
                    with open(filepath, "wb") as f:
                        f.write(img_bytes)
                   
                    count += 1
                    print(f"[{count}] Saved {filename} ({file_size/1024:.1f} KB) - {valid_msg}")
                   
                    # Verify metadata structure (rules list vs old rule dict)
                    if "rules" in metadata:
                        print(f"    ℹ️  Rules: {len(metadata['rules'])} usecases attached")
                    elif "rule" in metadata:
                         print(f"    ⚠️  WARNING: Found old 'rule' field instead of 'rules'!")
                else:
                    print(f"⚠️ Message received but no image data found. ID: {frame_id}")
 
            except json.JSONDecodeError:
                print("❌ Failed to decode JSON payload")
            except Exception as e:
                print(f"❌ Error processing message: {e}")
 
    except KeyboardInterrupt:
        print("\n🛑 Stopping consumer...")
    finally:
        consumer.close()
 
if __name__ == "__main__":
    main()
 
 