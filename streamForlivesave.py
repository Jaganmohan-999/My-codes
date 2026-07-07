import csv
import json
from urllib.parse import urlparse

def extract_rtsp_details(rtsp_url):
    parsed = urlparse(rtsp_url)

    # Extract username and password
    username = parsed.username
    password = parsed.password

    # Extract IP and port
    ip = parsed.hostname
    port = parsed.port

    # Extract channel (assuming last number in path is channel)
    path_parts = parsed.path.strip("/").split("/")
    channel = None
    for part in reversed(path_parts):
        if part.isdigit():
            channel = int(part)
            break

    return {
        "username": username,
        "password": password,
        "ip": ip,
        "port": str(port),
        "channels": [channel] if channel else []
    }


input_file = "rtsp_urls.csv"
output_file = "output.json"

output_data = []

with open(input_file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        rtsp_url = row["rtsp_url"]
        result = extract_rtsp_details(rtsp_url)
        output_data.append(result)

# Write to JSON file
with open(output_file, "w") as jsonfile:
    json.dump(output_data, jsonfile, indent=4)

print("Conversion completed. Check output.json")