import os
import cv2
import time
import pandas as pd

# -------- SETTINGS --------
input_file = r"D:\Bnew\Frames"   # Your Excel file
output_folder = r"D:\Bnew\Frames\ouptut"  # folder to save snapshots
os.makedirs(output_folder, exist_ok=True)

# Retry settings
MAX_RETRIES = 5
RETRY_DELAY = 2  # seconds


# -------- FUNCTION: Clean filename --------
def clean_name(text):
    return "".join(c if c.isalnum() or c in (" ", "_") else "_" for c in str(text)).strip().replace(" ", "_")


# -------- FUNCTION: Capture frame with retry --------
def capture_snapshot(rtsp_url):
    for attempt in range(MAX_RETRIES):
        print(f"Attempt {attempt+1}: Connecting...")

        cap = cv2.VideoCapture(rtsp_url)

        if not cap.isOpened():
            print("Connection failed, retrying...")
            time.sleep(RETRY_DELAY)
            continue

        # Give stream time to initialize
        time.sleep(2)

        ret, frame = cap.read()
        cap.release()

        if ret:
            return frame
        else:
            print("Frame capture failed, retrying...")
            time.sleep(RETRY_DELAY)

    return None


# -------- MAIN --------
def main():
    df = pd.read_excel(input_file)

    # Clean column names (removes hidden spaces)
    df.columns = df.columns.str.strip()

    print("Detected Columns:", df.columns.tolist())

    for index, row in df.iterrows():
        try:
            location = clean_name(row["Location"])
            camera_name = clean_name(row["Camera Name"])
            rtsp_url = str(row["rtsp_url"]).strip()

            if not rtsp_url.startswith("rtsp://"):
                print(f"Skipping invalid URL: {rtsp_url}")
                continue

            print(f"\nProcessing: {location} - {camera_name}")

            frame = capture_snapshot(rtsp_url)

            if frame is not None:
                filename = f"{location}_{camera_name}.jpg"
                output_path = os.path.join(output_folder, filename)

                cv2.imwrite(output_path, frame)
                print(f"Saved: {output_path}")
            else:
                print(f"Failed after retries: {rtsp_url}")

        except KeyError as e:
            print(f"Missing column in Excel: {e}")
        except Exception as e:
            print(f"Error in row {index}: {e}")

    print("\n✅ Done!")


if __name__ == "__main__":
    main()