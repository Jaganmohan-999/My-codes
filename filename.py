import os

main_path = r"D:\Training_RS\Train"
append_string = "q"

image_exts = [".jpg", ".jpeg", ".png", ".bmp", ".tif"]

for root, dirs, files in os.walk(main_path):

    if os.path.basename(root) == "images":

        folder_name = os.path.basename(os.path.dirname(root))
        labels_folder = os.path.join(os.path.dirname(root), "labels")

        for f in files:

            name, ext = os.path.splitext(f)

            if ext.lower() not in image_exts:
                continue

            # make globally unique name
            new_base = f"{name}_{folder_name}"

            # append user string
            final_base = new_base + append_string

            old_img = os.path.join(root, f)
            new_img = os.path.join(root, final_base + ext)

            os.rename(old_img, new_img)

            # rename label
            old_label = os.path.join(labels_folder, name + ".txt")
            new_label = os.path.join(labels_folder, final_base + ".txt")

            if os.path.exists(old_label):
                os.rename(old_label, new_label)

print("Finished renaming.")