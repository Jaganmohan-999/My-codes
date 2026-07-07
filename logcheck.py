import json
import subprocess
from datetime import datetime
from openpyxl import Workbook

# ===== CONFIG =====
EDGE_ID = "c6d13505c1e1fd96c7790f4c8b4c2e52"
JSON_FILE = r"D:\RS_logs\RS_cameraID.json"

# Time range (IMPORTANT: format must match docker logs format)
SINCE = "2026-03-23T10:00:00"
UNTIL = "2026-03-24T10:30:00"

SSH_CMD = f'ssh -i "D:\E2E\e2enodekey" root@216.48.180.230 "docker logs --since {SINCE} --until {UNTIL} compression-service 2>&1"'

OUTPUT_EXCEL = r"D:\RS_logs\output\output.xlsx"

ERROR_KEYWORDS = ["error", "failed", "timeout", "unauthorized", "refused"]

# ==================

# Step 1: Load JSON
with open(JSON_FILE, "r") as f:
    data = json.load(f)

if isinstance(data, dict) and "data" in data:
    data = data["data"]

# Extract cameras
cameras = set()
for item in data:
    if item.get("edge_id") == EDGE_ID:
        cameras.add(item.get("camera_id"))

print(f"Total cameras for edge {EDGE_ID}: {len(cameras)}")

# Step 2: Fetch logs via SSH
print("Fetching logs...")
result = subprocess.run(SSH_CMD, shell=True, capture_output=True, text=True)
logs = result.stdout.splitlines()
print("Total log lines:", len(logs))

# Step 3: Analyze (optimized single pass)
camera_status = {cam: {"found": False, "errors": []} for cam in cameras}

for line in logs:
    for cam in cameras:
        if cam in line:
            camera_status[cam]["found"] = True
            if any(err in line.lower() for err in ERROR_KEYWORDS):
                camera_status[cam]["errors"].append(line.strip())

# Step 4: Prepare results
results = []

for cam, data in camera_status.items():
    if not data["found"]:
        status = "MISSING"
    elif data["errors"]:
        status = "ERROR"
    else:
        status = "OK"

    error_sample = data["errors"][0] if data["errors"] else ""

    results.append([cam, status, error_sample])

# Step 5: Write to Excel
wb = Workbook()
ws = wb.active
ws.title = "Camera Status"

# Header
ws.append(["Camera ID", "Status", "Sample Error"])

# Rows
for row in results:
    ws.append(row)

# Save
wb.save(OUTPUT_EXCEL)

print(f"\nExcel saved at: {OUTPUT_EXCEL}")