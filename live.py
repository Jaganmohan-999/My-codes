import subprocess

# 🔹 Put your RTSP URL here
rtsp_url = "rtsp://RSDNJ:rsdn%40654321@183.82.99.55:1800/Streaming/Channels/201"
            


# Play the stream
subprocess.run([
    "ffplay",
    "-rtsp_transport", "tcp",
    "-i", rtsp_url
])