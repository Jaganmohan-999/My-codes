import os
import shutil

# -------- SETTINGS --------
source_folder = r"E:\Bnew\Frames"  # change this path

# -------- FUNCTION: Get folder name --------
def get_folder_name(filename):
    name, _ = os.path.splitext(filename)  # remove extension
    parts = name.split("_")

    if len(parts) >= 2 and parts[1].isdigit():
        # Example: Warangal_2_IPCAM → Warangal_2
        return f"{parts[0]}_{parts[1]}"
    else:
        # Example: Adilabad_IPCAM → Adilabad
        return parts[0]


# -------- MAIN --------
for filename in os.listdir(source_folder):
    file_path = os.path.join(source_folder, filename)

    # Skip directories
    if not os.path.isfile(file_path):
        continue

    # Skip files without underscore
    if "_" not in filename:
        print(f"Skipping (no underscore): {filename}")
        continue

    # Get folder name based on rule
    folder_name = get_folder_name(filename)

    # Create folder
    destination_folder = os.path.join(source_folder, folder_name)
    os.makedirs(destination_folder, exist_ok=True)

    # Move file
    destination_path = os.path.join(destination_folder, filename)
    shutil.move(file_path, destination_path)

    print(f"Moved: {filename} → {destination_folder}")

print("\n✅ Done!")