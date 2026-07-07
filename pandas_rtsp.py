import pandas as pd

STREAM_PATH = "stream1"   # change if needed

# Load CSV
#df = pd.read_csv(r"C:\Users\phani\Desktop\Camera_Details 22.02.2026.csv")
df = pd.read_csv(
    r"C:\Users\phani\Desktop\Camera_Details 22.02.2026.csv",
    encoding="latin1")

# Optional: remove duplicate rows (based on IP)
# df = df.drop_duplicates(subset=["ip"])

# Generate RTSP URL
df["rtsp_url"] = (
    "rtsp://"
    + df["Username"].astype(str)
    + ":"
    + df["Password"].astype(str)
    + "@"
    + df["Public IP"].astype(str)
    + ":"
    + df["RTSP Port"].astype(str)
    + "/"
)
df2 = df["rtsp_url"] 

# Print results
print(df["rtsp_url"])

# Optional: Save to file
df2.to_csv("rtsp_output.csv", index=False)