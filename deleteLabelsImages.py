import os

# ====== SET YOUR PATHS ======
images_dir = r"D:\RS_sorting\Phani -\183_82_1_179_cam1801\images" # Update this path to your images directory
labels_dir = r"D:\RS_sorting\Phani -\183_82_1_179_cam1801\labels" # Update this path to your labels directory
image_extensions = [".jpg", ".jpeg", ".png", ".bmp"]

# Build image dictionary
image_files = {}
for file in os.listdir(images_dir):
    name, ext = os.path.splitext(file)
    if ext.lower() in image_extensions:
        image_files[name] = file

print("\nSelect Operation:")
print("1 - Delete labels without images")
print("2 - Delete empty (0KB) labels and their images")
print("3 - Run both")
print("4 - Preview only (no deletion)")

choice = input("Enter your choice (1/2/3/4): ").strip()

preview_mode = (choice == "4")
run_missing = choice in ["1", "3", "4"]
run_empty = choice in ["2", "3", "4"]

deleted_labels = 0
deleted_images = 0

for label_file in os.listdir(labels_dir):
    if not label_file.endswith(".txt"):
        continue

    label_path = os.path.join(labels_dir, label_file)
    label_name = os.path.splitext(label_file)[0]

    # ===== Option 1: Missing image =====
    if run_missing and label_name not in image_files:
        if preview_mode:
            print(f"[PREVIEW] Would delete label (no image): {label_file}")
        else:
            os.remove(label_path)
            print(f"Deleted label (no image): {label_file}")
            deleted_labels += 1
        continue

    # ===== Option 2: Empty label =====
    if run_empty and os.path.getsize(label_path) == 0:
        image_path = os.path.join(images_dir, image_files.get(label_name, ""))

        if preview_mode:
            print(f"[PREVIEW] Would delete empty label: {label_file}")
            if os.path.exists(image_path):
                print(f"[PREVIEW] Would delete image: {image_files[label_name]}")
        else:
            os.remove(label_path)
            deleted_labels += 1
            print(f"Deleted empty label: {label_file}")

            if os.path.exists(image_path):
                os.remove(image_path)
                deleted_images += 1
                print(f"Deleted image: {image_files[label_name]}")

print("\n===== SUMMARY =====")
if not preview_mode:
    print(f"Total labels deleted: {deleted_labels}")
    print(f"Total images deleted: {deleted_images}")
else:
    print("Preview mode - No files were deleted.")