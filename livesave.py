import subprocess
import os
import concurrent.futures
from urllib.parse import quote

# ==============================
# SETTINGS
# ==============================

RECORD_SECONDS = 300
OUTPUT_DIR = r"D:\RS_Videos\Videos"
MAX_PARALLEL_RECORDINGS = 10  # limit simultaneous ffmpeg processes

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==============================
# DEFINE YOUR STREAMS HERE
# ==============================

STREAMS = [
    {
    "username": "SIPTJ",    #SI Patny
    "password": "sipt@654321",
    "ip": "183.82.98.202",
    "port": "1800",
    "channels": [101]
},
{
    "username": "SIKTPJ",   #SI Kothapet
    "password": "ktpjew@5202",
    "ip": "183.82.99.50",
    "port": "1800",
    "channels": [101]
},
{
    "username": "SIKTPJ",   #SI Kothapet
    "password": "ktpjew@5202",
    "ip": "183.82.99.50",
    "port": "1810",
    "channels": [101]
},
{
    "username": "SIMGJ",    #SI Madinaguda
    "password": "mgjew@654321",
    "ip": "183.82.114.243",
    "port": "1800",
    "channels": [101]
},
{
    "username": "RSDNJ",    #RS Dilsukhnagar
    "password": "rsdn@654321",
    "ip": "183.82.99.55",
    "port": "1800",
    "channels": [101]
},
{
    "username": "RSCNJ",    #RS Chandanagar
    "password": "rscn@2024",
    "ip": "183.82.99.77",
    "port": "1810",
    "channels": [101]
},
{
    "username": "RSKPJ",    #RS Kukatpally
    "password": "rskp@2024",
    "ip": "183.82.99.76",
    "port": "1810",
    "channels": [101]
},
{
    "username": "SIHKJ",    #SI Hanamkonda
    "password": "sihk@654321",
    "ip": "183.82.111.79",
    "port": "1800",
    "channels": [101]
},
{
    "username": "SIVNJ",    #SI Vizianagaram
    "password": "sivn@654321",
    "ip": "106.51.53.65",
    "port": "1800",
    "channels": [101]
},
{
    "username": "SISCJ",    #SI Suchitra
    "password": "sisc@5202",
    "ip": "183.82.111.16",
    "port": "1800",
    "channels": [101]
},
{
    "username": "SIKPJ",    #SI Kukatpally
    "password": "sikp@5202",
    "ip": "183.82.1.179",
    "port": "1810",
    "channels": [101]
},
{
    "username": "SIKPJ",    #SI Kukatpally
    "password": "sikp@5202",
    "ip": "183.82.1.179",
    "port": "1880",
    "channels": [101]
},
{
    "username": "SIAPJ",    #SI Ameerpet
    "password": "siap@654321",
    "ip": "183.82.108.29",
    "port": "1800",
    "channels": [101]
},
{
    "username": "SIGBJ",    #Gachibowli
    "password": "sigb@2024",
    "ip": "183.82.113.163",
    "port": "1810",
    "channels": [101]
},
{
    "username": "SIUPJ",    #Uppal
    "password": "siup@5202",
    "ip": "183.82.120.205",
    "port": "1800",
    "channels": [101]
},
{
    "username": "SIRMJ",    #SI Rajahmundry
    "password": "sirm@654321",
    "ip": "106.51.5.131",
    "port": "1800",
    "channels": [101]
},
{
    "username": "SIRMJ",    #SI Rajahmundry
    "password": "sirm@654321",
    "ip": "106.51.5.131",
    "port": "10081",
    "channels": [101]
},
{
    "username": "RSAPJ",    #RS Ameerpet
    "password": "rsap@5202",
    "ip": "183.82.99.146",
    "port": "1800",
    "channels": [101]
},
{
    "username": "RSAPJ",    #RS Ameerpet
    "password": "rsap@5202",
    "ip": "183.82.99.146",
    "port": "1810",
    "channels": [101]
}

]

# ==============================
# RECORD FUNCTION
# ==============================

def record_stream(stream_config, channel):
    try:
        username = stream_config["username"]
        password = quote(stream_config["password"])  # auto-encode special characters
        ip = stream_config["ip"]
        port = stream_config["port"]

        rtsp_url = f"rtsp://{username}:{password}@{ip}:{port}/Streaming/Channels/{channel}"
        output_file = os.path.join(
            OUTPUT_DIR,
            f"{ip.replace('.', '_')}_cam{channel}.mp4"
        )

        print(f"[INFO] Recording {rtsp_url}")

        command = [
            "ffmpeg",
            "-rtsp_transport", "tcp",
            "-i", rtsp_url,
            "-t", str(RECORD_SECONDS),
            "-c:v", "copy",
            "-an",
            "-y",
            output_file
        ]

        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print(f"[SUCCESS] Finished cam {channel} from {ip}")

    except Exception as e:
        print(f"[ERROR] Camera {channel} from {stream_config['ip']} failed: {e}")


# ==============================
# MAIN EXECUTION
# ==============================

if __name__ == "__main__":

    print("\n🚀 Starting Parallel Recordings...\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_PARALLEL_RECORDINGS) as executor:
        futures = []

        for stream in STREAMS:
            for ch in stream["channels"]:
                futures.append(
                    executor.submit(record_stream, stream, ch)
                )

        # Wait for all to finish
        concurrent.futures.wait(futures)

    print("\n✅ All recordings completed.\n")
