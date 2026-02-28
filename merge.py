import os
import shutil

def merge_folders(input_root, output_root):
    # Create output images and labels folders
    output_images = os.path.join(output_root, "images")
    output_labels = os.path.join(output_root, "labels")

    os.makedirs(output_images, exist_ok=True)
    os.makedirs(output_labels, exist_ok=True)

    # Loop through all subfolders inside input_root
    for folder_name in os.listdir(input_root):
        folder_path = os.path.join(input_root, folder_name)

        if os.path.isdir(folder_path):
            images_path = os.path.join(folder_path, "images")
            labels_path = os.path.join(folder_path, "labels")

            # Move images
            if os.path.exists(images_path):
                for file in os.listdir(images_path):
                    src = os.path.join(images_path, file)
                    dst = os.path.join(output_images, file)

                    # Handle duplicate filenames
                    if os.path.exists(dst):
                        base, ext = os.path.splitext(file)
                        dst = os.path.join(output_images, f"{base}_{folder_name}{ext}")

                    shutil.move(src, dst)

            # Move labels
            if os.path.exists(labels_path):
                for file in os.listdir(labels_path):
                    src = os.path.join(labels_path, file)
                    dst = os.path.join(output_labels, file)

                    # Handle duplicate filenames
                    if os.path.exists(dst):
                        base, ext = os.path.splitext(file)
                        dst = os.path.join(output_labels, f"{base}_{folder_name}{ext}")

                    shutil.move(src, dst)

    print("✅ All files moved successfully!")

# ==== INPUT FROM USER ====
input_root = r"D:\RS_sorting\Phani -\Done"
output_root = r"D:\RS_sorting\Phani -\Done\output"
merge_folders(input_root, output_root)