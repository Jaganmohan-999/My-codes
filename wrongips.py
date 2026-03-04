import pandas as pd
from urllib.parse import urlparse
import os

# ==========================
# CONFIG
# ==========================

INPUT_EXCEL = r"C:\Users\phani\Downloads\Camera_Details 22.02.2026.xlsx"        # Your original file
OUTPUT_EXCEL = r"D:\Bnew\streamcheck\output_with_rtsp.xlsx"  # Desired output file path

IP_COLUMN = "Public IP"                  # Column name in Excel
PORT_COLUMN = "RTSP Port"              # Column name in Excel

# ==========================
# STEP 1: ENTER RTSP URLS
# ==========================

print("\nPaste RTSP URLs (one per line).")
print("When finished, press ENTER on empty line:\n")

rtsp_urls = []

while True:
    line = input()
    if line.strip() == "":
        break
    rtsp_urls.append(line.strip())

# ==========================
# STEP 2: CREATE LOOKUP DICTIONARY
# ==========================

rtsp_map = {}

for url in rtsp_urls:
    parsed = urlparse(url)
    ip = parsed.hostname
    port = parsed.port

    if ip and port:
        key = f"{ip}:{port}"
        rtsp_map[key] = url

# ==========================
# STEP 3: READ EXCEL
# ==========================

df = pd.read_excel(INPUT_EXCEL)

# Ensure Port column is string for safe matching
df[PORT_COLUMN] = df[PORT_COLUMN].astype(str)

# ==========================
# STEP 4: MATCH AND ADD COLUMN
# ==========================

def match_rtsp(row):
    key = f"{row[IP_COLUMN]}:{row[PORT_COLUMN]}"
    return rtsp_map.get(key, "")

df["RTSP_URL"] = df.apply(match_rtsp, axis=1)

# ==========================
# STEP 5: SAVE OUTPUT
# ==========================

df.to_excel(OUTPUT_EXCEL, index=False)

print(f"\n✅ Output saved to: {os.path.abspath(OUTPUT_EXCEL)}\n")