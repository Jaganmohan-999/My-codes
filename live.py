import subprocess

# 🔹 Put your RTSP URL here
rtsp_url = "rtsp://SIPTJ:sipt%40654321@183.82.98.202:1800/Streaming/Channels/401"

# Play the stream
subprocess.run([
    "ffplay",
    "-rtsp_transport", "tcp",
    "-i", rtsp_url
])