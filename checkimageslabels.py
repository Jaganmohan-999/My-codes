import os

# =========================
# 🔧 SET YOUR PATHS HERE
# =========================

IMAGE_FOLDER = r"E:\Manoj\images"
LABEL_FOLDER = r"E:\Manoj\labels"


# =========================
# 🚀 MAIN FUNCTION
# =========================

def find_images_without_labels(image_folder, label_folder):
    missing_images = []

    # Get all label filenames (without extension)
    label_names = {
        os.path.splitext(f)[0].lower().strip()
        for f in os.listdir(label_folder)
        if f.endswith(".txt")   # change if needed (.xml, .json)
    }

    # Check each image
    for file in os.listdir(image_folder):
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
            image_name = os.path.splitext(file)[0].lower().strip()

            if image_name not in label_names:
                missing_images.append(file)  # keep full filename

    return missing_images


# =========================
# ▶️ RUN
# =========================

if __name__ == "__main__":
    missing = find_images_without_labels(IMAGE_FOLDER, LABEL_FOLDER)

    print("\n📌 Images WITHOUT labels:\n")

    for img in missing:
        print(img)

    print(f"\n✅ Total images without labels: {len(missing)}")