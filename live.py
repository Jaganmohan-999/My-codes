import subprocess

# 🔹 Put your RTSP URL here
rtsp_url = "rtsp://admin:admin@123@103.90.158.250:1554/cam/realmonitor?channel=1&subtype=0"

# Play the stream
subprocess.run([
    "ffplay",
    "-rtsp_transport", "tcp",
    "-i", rtsp_url
])