import subprocess

# 🔹 Put your RTSP URL here
rtsp_url = "rtsp://SIVNJ:sivn@654321@106.51.53.65:1800/Streaming/Channels/1001"

# Play the stream
subprocess.run([
    "ffplay",
    "-rtsp_transport", "tcp",
    "-i", rtsp_url
])