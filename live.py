import subprocess

# 🔹 Put your RTSP URL here
rtsp_url = "rtsp://admin:admin123@136.232.229.178:3008/cam/realmonitor?channel=3&subtype=0"

            
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