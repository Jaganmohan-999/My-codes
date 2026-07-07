import cv2
import os
from moviepy.video.io.VideoFileClip import VideoFileClip


def preview_and_select(video_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error opening video")
        return None, None

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    paused = False
    start_time = None
    end_time = None

    last_frame = None
    last_valid_time = 0

    print("\nControls:")
    print("s -> mark START")
    print("e -> mark END")
    print("space -> pause/resume")
    print("d -> forward 5 sec")
    print("a -> backward 5 sec")
    print("f -> forward 30 sec")
    print("b -> backward 30 sec")
    print("q -> quit preview\n")

    while True:
        if not paused:
            ret, frame = cap.read()

            if not ret:
                print("Reached end of video. Use a/b to go back or q to quit.")
                paused = True

                # keep last frame visible
                frame = last_frame

                # preserve actual last valid timestamp
                current_time = last_valid_time

            else:
                last_frame = frame
                current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
                last_valid_time = current_time

        else:
            current_time = last_valid_time

        # Show frame
        if last_frame is not None:
            display_frame = last_frame.copy()

            cv2.putText(
                display_frame,
                f"Current: {current_time:.2f}s / {duration:.2f}s",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            if start_time is not None:
                cv2.putText(
                    display_frame,
                    f"Start: {start_time:.2f}s",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 0, 0),
                    2
                )

            if end_time is not None:
                cv2.putText(
                    display_frame,
                    f"End: {end_time:.2f}s",
                    (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )

            cv2.imshow("Video Preview", display_frame)

        key = cv2.waitKey(30) & 0xFF

        # Mark START
        if key == ord('s'):
            start_time = last_valid_time
            print(f"Start marked at {start_time:.2f}s")

        # Mark END
        elif key == ord('e'):
            end_time = last_valid_time
            print(f"End marked at {end_time:.2f}s")

        # Pause / Resume
        elif key == ord(' '):
            paused = not paused
            print("Paused" if paused else "Resumed")

        # Forward 5 sec
        elif key == ord('d'):
            new_time = min(last_valid_time + 5, duration)
            cap.set(cv2.CAP_PROP_POS_MSEC, new_time * 1000)
            paused = False

        # Backward 5 sec
        elif key == ord('a'):
            new_time = max(last_valid_time - 5, 0)
            cap.set(cv2.CAP_PROP_POS_MSEC, new_time * 1000)
            paused = False

        # Forward 30 sec
        elif key == ord('f'):
            new_time = min(last_valid_time + 30, duration)
            cap.set(cv2.CAP_PROP_POS_MSEC, new_time * 1000)
            paused = False

        # Backward 30 sec
        elif key == ord('b'):
            new_time = max(last_valid_time - 30, 0)
            cap.set(cv2.CAP_PROP_POS_MSEC, new_time * 1000)
            paused = False

        # Quit preview
        elif key == ord('q'):
            print("Exiting preview...")
            break

    cap.release()
    cv2.destroyAllWindows()

    return start_time, end_time


# --------------------------
# Input / Output paths
# --------------------------
input_path = "/Users/tp-01/Documents/Record_Mobile/record_20260701_180642.mp4"

output_folder = "/Volumes/HARDDISK_2/CBT_DATA/annot/"
os.makedirs(output_folder, exist_ok=True)

output_path = os.path.join(
    output_folder,
    "NVR_ch5_main_20260610160002_20260610170001_2.mp4"
)


# --------------------------
# Select timestamps
# --------------------------
start_sec, end_sec = preview_and_select(input_path)


# --------------------------
# Validation
# --------------------------
if start_sec is None or end_sec is None:
    print("Start/end not selected properly. No video trimmed.")
    exit()

if start_sec >= end_sec:
    print("Invalid selection: start must be less than end.")
    exit()


print(f"\nTrimming from {start_sec:.2f}s to {end_sec:.2f}s")


# --------------------------
# Trim video
# --------------------------
clip = VideoFileClip(input_path)

trimmed = clip.subclipped(start_sec, end_sec)

trimmed.write_videofile(
    output_path,
    codec="libx264",
    audio_codec="aac",
    logger="bar"
)

trimmed.close()
clip.close()

print(f"Trimmed video saved at: {output_path}")