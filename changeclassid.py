import os

# 🔹 Set your folder path
folder_path = r"D:\RS_sorting\Phani\183_82_98_202_cam301\labels" # Update this path to your directory

# 🔹 Set what to change
OLD_CLASS_ID = "1"   # change FROM this
NEW_CLASS_ID = "0"   # change TO this

for filename in os.listdir(folder_path):
    if filename.endswith(".txt"):
        file_path = os.path.join(folder_path, filename)

        with open(file_path, "r") as file:
            lines = file.readlines()

        updated_lines = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) > 0 and parts[0] == OLD_CLASS_ID:
                parts[0] = NEW_CLASS_ID

            updated_lines.append(" ".join(parts) + "\n")

        with open(file_path, "w") as file:
            file.writelines(updated_lines)

print("All matching class IDs updated successfully!")