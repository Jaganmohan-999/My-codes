import subprocess
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from openpyxl import Workbook

# ==========================
# CONFIGURATION
# ==========================

RTSP_URLS = [
"rtsp://admin:Admin@123@103.90.156.247:1554/cam/realmonitor?channel=1&subtype=0",
"rtsp://admin:Admin@123@103.90.156.247:1555/cam/realmonitor?channel=1&subtype=0",
"rtsp://admin:Admin@123@202.62.71.157:1554/cam/realmonitor?channel=1&subtype=0",
"rtsp://admin:Admin@123@202.62.71.157:1555/cam/realmonitor?channel=1&subtype=0",
"rtsp://admin:Admin123@103.164.208.52:1555/cam/realmonitor?channel=1&subtype=0",
"rtsp://admin:Admin@123@175.101.145.164:1554/cam/realmonitor?channel=1&subtype=0",
"rtsp://admin:Admin@123@175.101.145.164:1555/cam/realmonitor?channel=1&subtype=0"


]

PARALLEL_CHECKS = 5
CHECK_SECONDS = 5
TIMEOUT_SECONDS = 30

OUTPUT_FOLDER = r"D:\Bnew\streamcheck"  # 🔥 Change if needed


# ==========================
# STREAM CHECK FUNCTION
# ==========================

def check_stream(rtsp_url):
    command = [
    "ffmpeg",
    "-rtsp_transport", "tcp",
    "-loglevel", "error",      # 🔥 move here
    "-t", str(CHECK_SECONDS),
    "-i", rtsp_url,
    "-map", "0:v:0",
    "-f", "null",
    "-"                        # output must be LAST
]

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=TIMEOUT_SECONDS
        )

        if result.returncode == 0:
            return (rtsp_url, "PASS", "")
        else:
            error_msg = result.stderr.decode().strip().split("\n")[-1]
            return (rtsp_url, "FAIL", error_msg)

    except subprocess.TimeoutExpired:
        return (rtsp_url, "FAIL", "Timeout expired")
    except Exception as e:
        return (rtsp_url, "FAIL", str(e))


# ==========================
# MAIN
# ==========================

def main():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(
        OUTPUT_FOLDER,
        f"rtsp_stream_report_{timestamp}.xlsx"
    )

    results = []

    with ThreadPoolExecutor(max_workers=PARALLEL_CHECKS) as executor:
        futures = [executor.submit(check_stream, url) for url in RTSP_URLS]

        for future in as_completed(futures):
            results.append(future.result())

    # Create Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "RTSP Report"

    # Header
    ws.append(["RTSP URL", "Status", "Error Message"])

    # Rows
    for row in results:
        ws.append(row)

    wb.save(output_file)

    print(f"\nExcel report saved at:\n{output_file}")


if __name__ == "__main__":
    main()