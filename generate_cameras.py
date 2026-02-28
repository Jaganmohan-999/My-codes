import json
from urllib.parse import urlparse, unquote

# 🔹 Paste your RTSP URLs here
rtsp_urls = [
    
   
]

# 🔹 Static IDs (modify if needed)
location_id = "6bf922d4-05d7-4158-8a43-dcca062fa1b7"
company_id = "27a060d5-0ff9-4c50-a9c5-db756f275e76"
device_id = "699d70384fb094c5470c6ba7"
zone_id = "699d7116555f209583a39812"
manufacturer = "69774ed70a254e273f969e92"

def pad_number(num):
    return str(num).zfill(3)

def parse_rtsp(rtsp_url):
    parsed = urlparse(rtsp_url)

    username = unquote(parsed.username) if parsed.username else ""
    password = unquote(parsed.password) if parsed.password else ""

    return {
        "username": username,
        "password": password,
        "ipAddress": parsed.hostname,
        "port": parsed.port,
        "path": parsed.path
    }

cameras = []

for index, rtsp_url in enumerate(rtsp_urls):
    parsed_data = parse_rtsp(rtsp_url)
    number = pad_number(index + 1)

    camera_json = {
        "cameraNumber": f"NUM{number}",
        "cameraName": f"CAM{number}",
        "username": parsed_data["username"],
        "password": parsed_data["password"],
        "ipAddress": parsed_data["ipAddress"],
        "path": parsed_data["path"],
        "rtspUrl": rtsp_url,
        "port": parsed_data["port"],
        "locationId": location_id,
        "companyId": company_id,
        "deviceId": device_id,
        "zoneId": zone_id,
        "manufacturer": manufacturer,
        "liveEnabled": False,
        "isPortForwarded": True,
        "macId": ""
    }

    cameras.append(camera_json)

# 🔥 Save JSON file in same folder
with open("cameras.json", "w") as f:
    json.dump(cameras, f, indent=4)

print("✅ cameras.json file created successfully.")