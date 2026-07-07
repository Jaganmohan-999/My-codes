from ultralytics import YOLO
import cv2
 
# Load your finetuned model
model = YOLO(r"D:\models_list\11n\best.pt")   # path to your trained weights
 
# Read frame (image)
frame = cv2.imread("image.png")
 
# Run inference
results = model(frame)
 
# Get the frame with bounding boxes drawn
annotated_frame = results[0].plot()
 
# Save result
cv2.imwrite("inferenced_frame.jpg", annotated_frame)
 
# Or display
cv2.imshow("Inference", annotated_frame)
cv2.waitKey(0)
cv2.destroyAllWindows()