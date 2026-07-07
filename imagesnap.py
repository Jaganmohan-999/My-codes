import os
import cv2
import csv
import json
import subprocess
from urllib.parse import urlparse

# ================= CONFIG =================
INPUT_FILE = r""   # optional (txt/csv/json/xlsx). Leave empty if using DIRECT_URLS
OUTPUT_FOLDER = r"/Users/tp-01/Documents/VS_outputs/Sample_frames/RS_Ameerpet"
DIRECT_URLS = [
rtsp://RSAPJ:rsap%405202@183.82.99.146:1800/Streaming/Channels/101
rtsp://RSAPJ:rsap%405202@183.82.99.146:1800/Streaming/Channels/201
rtsp://RSAPJ:rsap%405202@183.82.99.146:1800/Streaming/Channels/301
rtsp://RSAPJ:rsap%405202@183.82.99.146:1800/Streaming/Channels/401
rtsp://RSAPJ:rsap%405202@183.82.99.146:1800/Streaming/Channels/501
rtsp://RSAPJ:rsap%405202@183.82.99.146:1800/Streaming/Channels/601
rtsp://RSAPJ:rsap%405202@183.82.99.146:1800/Streaming/Channels/701
rtsp://RSAPJ:rsap%405202@183.82.99.146:1800/Streaming/Channels/801
rtsp://RSAPJ:rsap%405202@183.82.99.146:1800/Streaming/Channels/901
rtsp://RSAPJ:rsap%405202@183.82.99.146:1800/Streaming/Channels/1001
rtsp://RSAPJ:rsap%405202@183.82.99.146:1800/Streaming/Channels/1101
rtsp://RSAPJ:rsap%405202@183.82.99.146:1800/Streaming/Channels/1201
rtsp://RSAPJ:rsap%405202@183.82.99.146:1800/Streaming/Channels/1301
rtsp://RSAPJ:rsap%405202@183.82.99.146:1800/Streaming/Channels/1401
rtsp://RSAPJ:rsap%405202@183.82.99.146:1800/Streaming/Channels/1501
rtsp://RSAPJ:rsap%405202@183.82.99.146:1800/Streaming/Channels/1601
rtsp://RSAPJ:rsap%405202@183.82.99.146:1800/Streaming/Channels/1701
rtsp://RSAPJ:rsap%405202@183.82.99.146:1800/Streaming/Channels/1801
rtsp://RSAPJ:rsap%405202@183.82.99.146:1800/Streaming/Channels/190


]
# ==========================================

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# -------- SAFE FILE OPEN --------
def safe_open(file_path):
    for enc in ["utf-8", "cp1252", "latin-1"]:
        try:
            return open(file_path, "r", encoding=enc)
        except:
            continue
    return open(file_path, "r", encoding="utf-8", errors="ignore")


# -------- LOAD URLS --------
def load_rtsp_urls(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    urls = []

    if ext == ".txt":
        with safe_open(file_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("rtsp://"):
                    urls.append(line)

    elif ext == ".csv":
        with safe_open(file_path) as f:
            reader = csv.reader(f)
            for row in reader:
                for col in row:
                    if isinstance(col, str) and col.startswith("rtsp://"):
                        urls.append(col.strip())

    elif ext == ".json":
        with safe_open(file_path) as f:
            data = json.load(f)
            for item in data:
                if isinstance(item, dict):
                    url = item.get("rtspUrl") or item.get("url")
                    if url:
                        urls.append(url)

    elif ext == ".xlsx":
        try:
            import openpyxl
            wb = openpyxl.load_workbook(file_path)
            sheet = wb.active

            for row in sheet.iter_rows(values_only=True):
                for cell in row:
                    if isinstance(cell, str) and cell.startswith("rtsp://"):
                        urls.append(cell.strip())
        except ImportError:
            print("Install openpyxl for Excel support: pip install openpyxl")

    return urls


# -------- NAME GENERATOR --------
def parse_rtsp(rtsp_url):
    try:
        parsed = urlparse(rtsp_url)

        username = parsed.username or "cam"
        host = parsed.hostname or "ip"
        port = parsed.port or "554"

        # ---- Extract channel ----
        channel = "ch"

        # 1. Try query (channel=1)
        if parsed.query:
            for param in parsed.query.split("&"):
                if "channel=" in param.lower():
                    channel = param.split("=")[-1]
                    break

        # 2. Try path (/Streaming/Channels/101)
        if channel == "ch":
            parts = parsed.path.split("/")
            for p in reversed(parts):
                if p.isdigit():
                    channel = p
                    break

        # fallback unique hash if still same
        unique_part = channel

        name = f"{username}_{host}_{port}_{unique_part}"
        return name.replace(".", "_")

    except:
        return "camera"


# -------- SNAPSHOT USING OPENCV --------
def capture_opencv(rtsp_url, output_path):
    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)

    if not cap.isOpened():
        return False

    ret, frame = cap.read()
    cap.release()

    if ret:
        cv2.imwrite(output_path, frame)
        return True

    return False


# -------- SNAPSHOT USING FFMPEG --------
def capture_ffmpeg(rtsp_url, output_path):
    command = [
        "ffmpeg",
        "-rtsp_transport", "tcp",
        "-i", rtsp_url,
        "-frames:v", "1",
        "-y",
        output_path
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return result.returncode == 0


# -------- MAIN --------
def main():
    rtsp_urls = []

    # Priority: DIRECT_URLS > FILE
    if DIRECT_URLS:
        rtsp_urls.extend(DIRECT_URLS)

    elif INPUT_FILE:
        rtsp_urls.extend(load_rtsp_urls(INPUT_FILE))

    if not rtsp_urls:
        print("No RTSP URLs found!")
        return

    print(f"Found {len(rtsp_urls)} cameras\n")

    for i, rtsp_url in enumerate(rtsp_urls, start=1):
        print(f"[{i}] Connecting: {rtsp_url}")

        filename = parse_rtsp(rtsp_url) + ".jpg"
        output_path = os.path.join(OUTPUT_FOLDER, filename)

        # Try OpenCV first
        if capture_opencv(rtsp_url, output_path):
            print("Saved (OpenCV):", output_path)
        else:
            print("OpenCV failed, trying FFmpeg...")

            if capture_ffmpeg(rtsp_url, output_path):
                print("Saved (FFmpeg):", output_path)
            else:
                print("❌ Failed completely")

    print("\nDone!")


if __name__ == "__main__":
    main()