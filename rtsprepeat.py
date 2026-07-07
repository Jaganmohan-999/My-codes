import pandas as pd

# Load Excel file
file_path = r"C:\Users\phani\Downloads\BNewrtsp\BNewrtsp\bnew_rtsp 2.xlsx" # change this to your file path
df = pd.read_excel(file_path)

# Find rows where rtsp_url is duplicated (keep all occurrences)
duplicates = df[df.duplicated(subset=["rtsp_url"], keep=False)]

# Select only required columns
result = duplicates[["cameraName", "rtsp_url", "cameraNumber"]]

# Sort for readability (optional)
result = result.sort_values(by="rtsp_url")

# Print result
print(result)

# Save to a new Excel file (optional)
result.to_excel("duplicate_rtsp_urls.xlsx", index=False)