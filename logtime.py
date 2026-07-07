import subprocess
import re
import json

# ---------- CONFIG ----------
SSH_KEY = r"D:\E2E\e2enodekey"   # ✅ raw string (important)
USER = "root"
HOST = "1164.52.196.230"
CONTAINER = "compression-service"   # 🔁 change this

TARGET_EDGE_ID = "c6d13505c1e1fd96c7790f4c8b4c2e52"

JSON_FILE = r"D:\RS_logs\Surveillance_Global.cameras_configurations (6).json"


# ---------- LOAD JSON ----------
def load_records():
    with open(JSON_FILE, "r") as f:
        return json.load(f)


# ---------- GET CAMERAS FOR EDGE ----------
def get_cameras_for_edge(records, edge_id):
    cameras = set()

    for r in records:
        if r.get("edge_id") == edge_id:
            cameras.add(r.get("camera_id"))

    return cameras


# ---------- FETCH LOGS USING SSH ----------
def fetch_logs(camera_ids):
    if not camera_ids:
        print("❌ No cameras found for this edge")
        return []

    # Build grep pattern
    cam_pattern = "|".join(camera_ids)

    # ✅ Proper quoted SSH command (your requirement)
    command = f'''
    ssh -i "{SSH_KEY}" {USER}@{HOST} "docker logs {CONTAINER} 2>&1 | tail -n 2000"
    '''

    print("\n🚀 Running SSH command...")
    print(command)

    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # 🔍 DEBUG OUTPUT
    print("\n--- STDOUT (logs preview) ---")
    print(result.stdout[:1000])

    print("\n--- STDERR ---")
    print(result.stderr)

    return result.stdout.splitlines()


# ---------- PARSE LOGS ----------
def parse_logs(log_lines, camera_ids):
    camera_times = {}

    for line in log_lines:
        if "cam=" not in line:
            continue

        cam_match = re.search(r'cam=([a-z0-9]+)', line)
        total_match = re.search(r'total=([\d.]+)ms', line)

        if cam_match and total_match:
            cam_id = cam_match.group(1)

            if cam_id in camera_ids:
                camera_times[cam_id] = float(total_match.group(1))

    return camera_times


# ---------- MAIN ----------
def main():
    print("📄 Loading JSON...")
    records = load_records()

    # 🎯 Step 1: Get cameras for specific edge
    camera_ids = get_cameras_for_edge(records, TARGET_EDGE_ID)

    print(f"\n📷 Cameras for edge {TARGET_EDGE_ID}:")
    for cam in camera_ids:
        print("  ", cam)

    # 🎯 Step 2: Fetch logs from server
    log_lines = fetch_logs(camera_ids)

    if not log_lines:
        print("\n❌ No logs fetched. Check SSH / container.")
        return

    # 🎯 Step 3: Parse logs
    camera_times = parse_logs(log_lines, camera_ids)

    # 🎯 Step 4: Compute results
    total_sum = sum(camera_times.values())
    max_latency = max(camera_times.values()) if camera_times else 0

    print("\n📊 FINAL RESULT")
    print("================================")

    print(f"Edge ID: {TARGET_EDGE_ID}")

    if not camera_times:
        print("⚠️ No matching camera logs found")
    else:
        for cam, t in camera_times.items():
            print(f"{cam} → {t} ms")

    print(f"\n🧮 Total Processing Time: {total_sum} ms")
    print(f"⚡ Pipeline Latency (max): {max_latency} ms")


# ---------- RUN ----------
if __name__ == "__main__":
    main()