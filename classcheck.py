from ultralytics import YOLO

model = YOLO(r"D:\models_list\11n\6-4\best.pt")

print(model.names)