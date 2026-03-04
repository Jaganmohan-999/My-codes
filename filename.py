import os

# ====== SETTINGS ======
root_directory = r"D:\RS_sorting\Phani\infer2"
numbers_to_add = "968"   # <-- numbers you want to append
# ======================

for folder_name in os.listdir(root_directory):

    old_folder_path = os.path.join(root_directory, folder_name)

    if not os.path.isdir(old_folder_path):
        continue

    # New folder name
    new_folder_name = folder_name + numbers_to_add
    new_folder_path = os.path.join(root_directory, new_folder_name)

    print(f"\nRenaming folder:")
    print(f"{folder_name}  ->  {new_folder_name}")

    # Rename outer folder first
    os.rename(old_folder_path, new_folder_path)

    # Now rename inside files
    for subfolder in ["images", "labels"]:
        subfolder_path = os.path.join(new_folder_path, subfolder)

        if not os.path.exists(subfolder_path):
            continue

        for filename in os.listdir(subfolder_path):

            old_file_path = os.path.join(subfolder_path, filename)

            if not os.path.isfile(old_file_path):
                continue

            name, ext = os.path.splitext(filename)
            counter = name.split("_")[-1]

            new_filename = f"{new_folder_name}_{counter}{ext}"
            new_file_path = os.path.join(subfolder_path, new_filename)

            os.rename(old_file_path, new_file_path)

            print(f"  {filename} -> {new_filename}")

print("\n✅ All folders and files updated successfully.")