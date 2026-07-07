import os

main_path = r"/Users/tp-01/Downloads/coco_fire_test/coco_ai_set"
image_exts = [".jpg", ".jpeg", ".png", ".bmp", ".tif"]

for folder in os.listdir(main_path):
    folder_path = os.path.join(main_path, folder)

    if not os.path.isdir(folder_path):
        continue

    images_folder = os.path.join(folder_path, "images")
    labels_folder = os.path.join(folder_path, "labels")

    if not os.path.exists(images_folder):
        continue

    files = sorted(os.listdir(images_folder))

    counter = 1

    for f in files:
        name, ext = os.path.splitext(f)

        if ext.lower() not in image_exts:
            continue

        # zero-padded numbering
        number = str(counter).zfill(5)

        new_base = f"{folder}_{number}"

        old_img = os.path.join(images_folder, f)
        new_img = os.path.join(images_folder, new_base + ext)

        os.rename(old_img, new_img)

        # rename label
        old_label = os.path.join(labels_folder, name + ".txt")
        new_label = os.path.join(labels_folder, new_base + ".txt")

        if os.path.exists(old_label):
            os.rename(old_label, new_label)

        counter += 1

print("Finished renaming.")