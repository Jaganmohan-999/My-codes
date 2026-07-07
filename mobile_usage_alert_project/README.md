# Mobile Usage Alert Project

This project detects people in a video, detects visible mobile phones, uses pose keypoints to estimate phone usage posture, and saves an annotated output video.

## Files

- `mobile_usage_alert.py`: main inference script
- `requirements.txt`: Python dependencies

## Install

```powershell
pip install -r requirements.txt
```

## Run

```powershell
python mobile_usage_alert.py `
  --video "D:\path\input.mp4" `
  --output "D:\path\output_mobile_alert.mp4" `
  --detector-model "D:\path\to\detector.pt" `
  --pose-model "D:\path\to\pose.pt"
```

## Notes

- Default `person` class is `0`
- Default `cell phone` class is `67`
- If your custom model uses different class ids, pass `--person-class` and `--phone-class`
- The script also writes a CSV log next to the output video
