import subprocess

# 🔹 Put your RTSP URL here
rtsp_url = "rtsp://SIRMJ:sirm%40654321@106.51.5.131:10081/Streaming/Channels/301"
            


# Play the stream
subprocess.run([
    "ffplay",
    "-rtsp_transport", "tcp",
    "-i", rtsp_url
])