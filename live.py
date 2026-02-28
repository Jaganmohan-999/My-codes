import subprocess

# 🔹 Put your RTSP URL here
rtsp_url = "rtsp://admin:paramount123@192.168.0.37:554/Streaming/Channels/101"

# Play the stream
subprocess.run([
    "ffplay",
    "-rtsp_transport", "tcp",
    "-i", rtsp_url
])