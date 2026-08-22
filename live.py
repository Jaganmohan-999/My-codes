import subprocess

# 🔹 Put your RTSP URL here
rtsp_url = "rtsp://admin:paramount@555@183.82.105.189:554/Streaming/Channels/1201"

            
# Play the stream
subprocess.run([
    "ffplay",
    "-rtsp_transport", "tcp",
    "-fflags", "nobuffer",
    "-flags", "low_delay",
    "-strict", "experimental",
    "-analyzeduration", "1000000",
    "-probesize", "1000000",
    "-loglevel", "debug",   # 👈 important for troubleshooting
    "-i", rtsp_url
])