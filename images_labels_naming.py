import os

# =====================================================
# CONFIGURATION
# =====================================================

MAIN_FOLDER = '/Users/tp-01/Documents/Annotation/Bnew/bnew3'

NEW_PREFIX = "bnew_25757"

# =====================================================

images_folder = os.path.join(
    MAIN_FOLDER,
    "images"
)

labels_folder = os.path.join(
    MAIN_FOLDER,
    "labels"
)

# Get all image files
image_files = sorted([
    f for f in os.listdir(images_folder)
    if f.lower().endswith(
        (".jpg", ".jpeg", ".png")
    )
])

print(f"Found {len(image_files)} images")

for idx, image_file in enumerate(image_files, start=1):

    image_name, image_ext = os.path.splitext(
        image_file
    )

    old_image_path = os.path.join(
        images_folder,
        image_file
    )

    old_label_path = os.path.join(
        labels_folder,
        image_name + ".txt"
    )

    new_image_name = (
        f"{NEW_PREFIX}_{idx}"
        f"{image_ext}"
    )

    new_label_name = (
        f"{NEW_PREFIX}_{idx}.txt"
    )

    new_image_path = os.path.join(
        images_folder,
        new_image_name
    )

    new_label_path = os.path.join(
        labels_folder,
        new_label_name
    )

    # Rename image
    os.rename(
        old_image_path,
        new_image_path
    )

    # Rename label if exists
    if os.path.exists(
        old_label_path
    ):
        os.rename(
            old_label_path,
            new_label_path
        )

print("\nRenaming completed successfully.")