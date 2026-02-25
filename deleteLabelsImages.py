# 1. Delete labels that don’t have a matching image
# 2. Delete labels that are 0 KB (empty files)
# 3. If a label is deleted because it's empty → also delete its corresponding image

import os

# ====== SET YOUR PATHS ======
images_dir = r"C:\path\to\images"
labels_dir = r"C:\path\to\labels"

# Supported image extensions
image_extensions = [".jpg", ".jpeg", ".png", ".bmp"]

# Get image basenames
image_files = {}
for file in os.listdir(images_dir):
    name, ext = os.path.splitext(file)
    if ext.lower() in image_extensions:
        image_files[name] = file

deleted_labels = 0
deleted_images = 0

for label_file in os.listdir(labels_dir):
    if not label_file.endswith(".txt"):
        continue

    label_path = os.path.join(labels_dir, label_file)
    label_name = os.path.splitext(label_file)[0]

    # ===== Condition 1: Label has no matching image =====
    if label_name not in image_files:
        os.remove(label_path)
        print(f"Deleted label (no image): {label_file}")
        deleted_labels += 1
        continue

    # ===== Condition 2: Label is 0 KB (empty) =====
    if os.path.getsize(label_path) == 0:
        # Delete label
        os.remove(label_path)
        deleted_labels += 1
        print(f"Deleted empty label: {label_file}")

        # Delete corresponding image
        image_path = os.path.join(images_dir, image_files[label_name])
        if os.path.exists(image_path):
            os.remove(image_path)
            deleted_images += 1
            print(f"Deleted corresponding image: {image_files[label_name]}")

print("\n===== SUMMARY =====")
print(f"Total labels deleted: {deleted_labels}")
print(f"Total images deleted: {deleted_images}")