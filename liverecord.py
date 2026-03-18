import subprocess
import threading
import os
from datetime import datetime

# ==========================
# CONFIGURATION
# ==========================

RTSP_URLS = [
"rtsp://RSDNJ:rsdn%40654321@183.82.99.55:1800/Streaming/Channels/901",
"rtsp://SIUPJ:siup%405202@183.82.120.205:1800/Streaming/Channels/1001",
"rtsp://SISCJ:sisc%405202@183.82.111.16:1800/Streaming/Channels/102",
"rtsp://SISCJ:sisc%405202@183.82.111.16:1800/Streaming/Channels/702",
"rtsp://RSDNJ:rsdn%40654321@183.82.99.55:1800/Streaming/Channels/201",
"rtsp://SIVNJ:sivn%40654321@106.51.53.65:1800/Streaming/Channels/301",
"rtsp://SIKTPJ:ktpjew%405202@183.82.99.50:1810/Streaming/Channels/101",
"rtsp://RSKPJ:rskp%402024@183.82.99.76:1810/Streaming/Channels/1201",
"rtsp://RSAPJ:rsap%405202@183.82.99.146:1800/Streaming/Channels/1001",
"rtsp://RSKPJ:rskp%402024@183.82.99.76:1810/Streaming/Channels/101",
"rtsp://SIHKJ:sihk%40654321@183.82.111.79:1800/Streaming/Channels/2501",
"rtsp://RSDNJ:rsdn%40654321@183.82.99.55:1800/Streaming/Channels/1201",
"rtsp://SIHKJ:sihk%40654321@183.82.111.79:1800/Streaming/Channels/1201",
"rtsp://RSKPJ:rskp%402024@183.82.99.76:1810/Streaming/Channels/1501"


]

RECORD_SECONDS = 300        # Recording duration per stream
PARALLEL_RECORDINGS = 2    # Number of parallel recordings

OUTPUT_FOLDER = r"D:\TPsol"


# ==========================
# RECORDING FUNCTION
# ==========================

def record_stream(rtsp_url, index):
    try:
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        # Generate date + timestamp (Windows safe format)
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

        output_file = os.path.join(
            OUTPUT_FOLDER,
            f"camera_{index}_{timestamp}.mp4"
        )

        command = [
            "ffmpeg",
            "-rtsp_transport", "tcp",
            "-i", rtsp_url,
            "-t", str(RECORD_SECONDS),
            "-c:v", "copy",   # Copy video without re-encoding
            "-an",            # Disable audio
            "-y",
            output_file
        ]

        print(f"[{timestamp}] Starting recording camera {index}...")

        subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        print(f"[{timestamp}] Finished recording camera {index}")

    except Exception as e:
        print(f"Error recording camera {index}: {e}")


# ==========================
# MAIN EXECUTION
# ==========================

def main():
    if not RTSP_URLS:
        print("No RTSP URLs configured.")
        return

    threads = []

    # Limit recordings to requested parallel count
    for i in range(min(PARALLEL_RECORDINGS, len(RTSP_URLS))):
        t = threading.Thread(
            target=record_stream,
            args=(RTSP_URLS[i], i)
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("All recordings completed.")


if __name__ == "__main__":
    main()