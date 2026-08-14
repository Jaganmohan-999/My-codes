import os
import uuid
from pathlib import Path

# =====================================================
# CONFIGURATION — CHANGE THESE
# =====================================================

# Main folder containing images/labels directly
# OR multiple folders containing images/labels
MAIN_FOLDER = r"/Users/tp-01/Downloads/dataset"

# Text to add after the folder name
SUFFIX = "fire"

# Starting number
START_NUMBER = 1

# =====================================================

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".tif",
    ".tiff"
}


def find_dataset_folders(main_folder):
    """
    Finds all folders containing both:
        images/
        labels/

    Supports:
        Main/images + Main/labels

    and:
        Main/Folder1/images + Main/Folder1/labels
        Main/Folder2/images + Main/Folder2/labels
    """

    main_folder = Path(main_folder)

    dataset_folders = []

    # Check whether the main folder itself contains
    # images and labels folders
    if (
        (main_folder / "images").is_dir()
        and
        (main_folder / "labels").is_dir()
    ):
        dataset_folders.append(main_folder)

    # Search all subfolders
    for folder in main_folder.rglob("*"):

        if not folder.is_dir():
            continue

        images_folder = folder / "images"
        labels_folder = folder / "labels"

        if (
            images_folder.is_dir()
            and
            labels_folder.is_dir()
        ):

            if folder not in dataset_folders:
                dataset_folders.append(folder)

    return sorted(dataset_folders)


def rename_dataset(dataset_folder):

    images_folder = dataset_folder / "images"
    labels_folder = dataset_folder / "labels"

    folder_name = dataset_folder.name

    print("\n" + "=" * 70)
    print(f"Processing folder: {folder_name}")
    print(f"Images: {images_folder}")
    print(f"Labels: {labels_folder}")

    # Get valid image files
    image_files = sorted(
        [
            file
            for file in images_folder.iterdir()
            if (
                file.is_file()
                and
                file.suffix.lower() in IMAGE_EXTENSIONS
                and
                not file.name.startswith("._")
            )
        ]
    )

    if not image_files:

        print("No images found. Skipping folder.")

        return

    rename_pairs = []

    missing_labels = []

    # Find matching labels
    for image_file in image_files:

        label_file = (
            labels_folder
            /
            f"{image_file.stem}.txt"
        )

        if not label_file.exists():

            missing_labels.append(
                image_file.name
            )

            continue

        rename_pairs.append(
            (
                image_file,
                label_file
            )
        )

    print(
        f"Matching image-label pairs: "
        f"{len(rename_pairs)}"
    )

    print(
        f"Images without labels: "
        f"{len(missing_labels)}"
    )

    if missing_labels:

        print("\nImages without matching labels:")

        for image_name in missing_labels:

            print(
                f"  {image_name}"
            )

    if not rename_pairs:

        print(
            "No matching image-label pairs found."
        )

        return

    # -----------------------------------------
    # STEP 1:
    # Rename to temporary unique names
    #
    # This prevents conflicts if target names
    # already exist.
    # -----------------------------------------

    temporary_pairs = []

    for image_file, label_file in rename_pairs:

        unique_id = uuid.uuid4().hex

        temporary_image = (
            images_folder
            /
            f"temporary_{unique_id}"
            f"{image_file.suffix.lower()}"
        )

        temporary_label = (
            labels_folder
            /
            f"temporary_{unique_id}.txt"
        )

        image_file.rename(
            temporary_image
        )

        label_file.rename(
            temporary_label
        )

        temporary_pairs.append(
            (
                temporary_image,
                temporary_label
            )
        )

    # -----------------------------------------
    # STEP 2:
    # Give final names
    # -----------------------------------------

    renamed_count = 0

    for number, pair in enumerate(
        temporary_pairs,
        start=START_NUMBER
    ):

        temporary_image = pair[0]

        temporary_label = pair[1]

        # Example:
        # Folder1_fire_1
        new_base_name = (
            f"{folder_name}"
            f"_{SUFFIX}"
            f"_{number}"
        )

        new_image_path = (
            images_folder
            /
            f"{new_base_name}"
            f"{temporary_image.suffix.lower()}"
        )

        new_label_path = (
            labels_folder
            /
            f"{new_base_name}.txt"
        )

        temporary_image.rename(
            new_image_path
        )

        temporary_label.rename(
            new_label_path
        )

        renamed_count += 1

        print(
            f"{renamed_count}: "
            f"{new_image_path.name} "
            f"<--> "
            f"{new_label_path.name}"
        )

    print(
        f"\nSuccessfully renamed "
        f"{renamed_count} image-label pairs."
    )


def main():

    main_folder = Path(
        MAIN_FOLDER
    ).expanduser()

    if not main_folder.exists():

        raise FileNotFoundError(
            f"Main folder not found:\n"
            f"{main_folder}"
        )

    dataset_folders = (
        find_dataset_folders(
            main_folder
        )
    )

    if not dataset_folders:

        raise FileNotFoundError(
            "\nNo folder containing both "
            "'images' and 'labels' was found.\n\n"
            "Expected structure:\n"
            "Main/images\n"
            "Main/labels\n\n"
            "OR:\n\n"
            "Main/Folder1/images\n"
            "Main/Folder1/labels"
        )

    print(
        f"\nFound "
        f"{len(dataset_folders)} "
        f"dataset folder(s)."
    )

    for dataset_folder in dataset_folders:

        rename_dataset(
            dataset_folder
        )

    print(
        "\n"
        + "=" * 70
    )

    print(
        "ALL FOLDERS COMPLETED"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":

    main()