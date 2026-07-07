import paramiko
import re
from datetime import datetime

# -------- CONFIG --------
HOST = "164.52.193.23"
USERNAME = "root"
PASSWORD = r"D:\E2E\e2enodekey"

LOG_WINDOW = "30m"

# -----------------------

FRAME_PATTERN = re.compile(r"(?:frame_id=|frame=|frame:\s*)([a-f0-9\-]+)")
EPOCH_PATTERN = re.compile(r"(\d{13})")
DATETIME_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})")


def extract_timestamp(line):
    m = EPOCH_PATTERN.search(line)
    if m:
        return int(m.group(1))

    m = DATETIME_PATTERN.search(line)
    if m:
        dt = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S,%f")
        return int(dt.timestamp() * 1000)

    return None


def parse_logs(log_text):
    data = {}
    for line in log_text.splitlines():
        frame_match = FRAME_PATTERN.search(line)
        if frame_match:
            frame_id = frame_match.group(1)
            ts = extract_timestamp(line)
            if ts:
                data.setdefault(frame_id, []).append(ts)
    return data


def fetch_logs(ssh, container):
    cmd = f"docker logs {container} --since {LOG_WINDOW}"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode()


def get_containers(ssh, keyword):
    cmd = "docker ps --format '{{.Names}}'"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    containers = stdout.read().decode().splitlines()

    return [c for c in containers if keyword in c]


def main():
    print("🔌 Connecting to server...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #ssh.connect(HOST, username=USERNAME, password=PASSWORD)
    ssh.connect(
    HOST,
    username=USERNAME,
    key_filename=r"D:\E2E\e2enodekey"
    )

    # 🔍 Detect containers
    inference_containers = get_containers(ssh, "inference-server-consumer")
    rule_containers = get_containers(ssh, "rule-engine")

    print("\n📦 Detected Inference Containers:")
    for c in inference_containers:
        print(f"   → {c}")

    print("\n📦 Detected Rule Engine Containers:")
    for c in rule_containers:
        print(f"   → {c}")

    # ------------------ FETCH LOGS ------------------
    print("\n📥 Fetching inference logs...")
    inf_logs = ""
    for c in inference_containers:
        try:
            inf_logs += fetch_logs(ssh, c)
        except:
            print(f"⚠️ Failed: {c}")

    print("\n📥 Fetching rule engine logs...")
    rule_logs = ""
    for c in rule_containers:
        try:
            rule_logs += fetch_logs(ssh, c)
        except:
            print(f"⚠️ Failed: {c}")

    ssh.close()

    # ------------------ PARSE ------------------
    print("\n🔍 Parsing logs...")

    inf_data = parse_logs(inf_logs)
    rule_data = parse_logs(rule_logs)

    print(f"Inference frames: {len(inf_data)}")
    print(f"Rule frames: {len(rule_data)}")

    print("\n📊 Delay Results:\n")

    delays = []
    MAX_DELAY = 5 * 60 * 1000  # 5 min

    for frame_id in inf_data:
        if frame_id in rule_data:

            inf_times = inf_data[frame_id]
            rule_times = sorted(rule_data[frame_id])

            
            for inf_ts in inf_times:
                # find closest rule timestamp AFTER inference
                
                valid_rules = [r for r in rule_times if r >= inf_ts]

                if valid_rules:
                    rule_ts = valid_rules[0]
                    delay = rule_ts - inf_ts

                    if 0 <= delay < MAX_DELAY:  
                        delays.append(delay)
                        print(f"{frame_id} → {delay} ms")

    if delays:
        print("\n📈 Summary:")
        print(f"Min: {min(delays)} ms")
        print(f"Max: {max(delays)} ms")
        print(f"Avg: {sum(delays)/len(delays):.2f} ms")
        print(f"Count: {len(delays)}")
    else:
        print("⚠️ No matching frames found")


if __name__ == "__main__":
    main()