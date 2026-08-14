import os
import cv2

# ==========================================
# INPUT
# ==========================================

# OPTION 1:
# Give a folder containing videos
INPUT_PATH = r"/Users/tp-01/Documents/Producer_TensorRT/test/untitled folder"

# OPTION 2:
# Or give individual video paths in order
VIDEO_FILES = [
    # r"/path/video1.mp4",
    # r"/path/video2.mp4",
]

OUTPUT_VIDEO = r"/Users/tp-01/Documents/Producer_TensorRT/test/footfall_uppal.mp4"

VIDEO_EXTENSIONS = (
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".dav"
)

# ==========================================
# PREPARE VIDEO LIST
# ==========================================

if os.path.isdir(INPUT_PATH):

    video_files = sorted([
        os.path.join(INPUT_PATH, f)
        for f in os.listdir(INPUT_PATH)
        if f.lower().endswith(VIDEO_EXTENSIONS)
    ])

elif os.path.isfile(INPUT_PATH):

    video_files = [INPUT_PATH]

elif len(VIDEO_FILES) > 0:

    video_files = VIDEO_FILES

else:

    raise Exception("No valid input provided.")

if len(video_files) == 0:
    raise Exception("No videos found.")

print("\nVideos to merge:\n")

for i, video in enumerate(video_files, start=1):
    print(f"{i}. {os.path.basename(video)}")

# ==========================================
# READ FIRST VIDEO
# ==========================================

cap = cv2.VideoCapture(video_files[0])

if not cap.isOpened():
    raise Exception(f"Cannot open {video_files[0]}")

fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

cap.release()

# ==========================================
# CREATE OUTPUT DIRECTORY
# ==========================================

os.makedirs(os.path.dirname(OUTPUT_VIDEO), exist_ok=True)

# ==========================================
# VIDEO WRITER
# ==========================================

fourcc = cv2.VideoWriter_fourcc(*"mp4v")

writer = cv2.VideoWriter(
    OUTPUT_VIDEO,
    fourcc,
    fps,
    (width, height)
)

if not writer.isOpened():
    raise Exception("Could not create output video.")

# ==========================================
# MERGE
# ==========================================

total_frames = 0

for video_path in video_files:

    print(f"\nProcessing: {os.path.basename(video_path)}")

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Skipping:", video_path)
        continue

    current_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    current_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    frame_count = 0

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        if current_width != width or current_height != height:
            frame = cv2.resize(frame, (width, height))

        writer.write(frame)

        frame_count += 1
        total_frames += 1

    cap.release()

    print(f"Frames merged: {frame_count}")

writer.release()

print("\n===================================")
print("✅ Merge completed successfully")
print(f"Videos merged : {len(video_files)}")
print(f"Total Frames  : {total_frames}")
print(f"Output        : {OUTPUT_VIDEO}")
print("===================================")