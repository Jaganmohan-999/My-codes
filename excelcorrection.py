import pandas as pd
import re

# Load Excel
file_path = r"C:\Users\phani\Desktop\cleaned_output.xlsx"
df = pd.read_excel(file_path)

RTSP_COL = "rtsp_url"
IP_COL = "ip"
PORT_COL = "port"

# --- Extract all RTSP (ip, port) pairs ---
def extract_ip_port(rtsp):
    if not isinstance(rtsp, str):
        return None
    
    match = re.search(r'@([\d\.]+)(?::(\d+))?', rtsp)
    if match:
        ip = match.group(1)
        port = match.group(2) if match.group(2) else "554"
        return (ip, port)
    return None

rtsp_set = set()
for url in df[RTSP_COL]:
    result = extract_ip_port(url)
    if result:
        rtsp_set.add(result)

# --- Check each IP+Port from columns ---
status_list = []

for _, row in df.iterrows():
    ip = str(row[IP_COL])
    port = str(row[PORT_COL]) if not pd.isna(row[PORT_COL]) else "554"

    if (ip, port) in rtsp_set:
        status_list.append("FOUND")
    else:
        status_list.append("MISSING")

df["status"] = status_list

# --- Save output ---
df.to_excel("rtsp_check_result.xlsx", index=False)

print("Done! Check rtsp_check_result.xlsx")