import subprocess

# 🔹 Put your RTSP URL here
rtsp_url = "rtsp://SIPTJ:sipt%405202@183.82.98.202:1800/Streaming/Channels/1101"
            


# Play the stream
subprocess.run([
    "ffplay",
    "-rtsp_transport", "tcp",
    "-i", rtsp_url
])