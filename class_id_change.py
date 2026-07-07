from pathlib import Path

MAIN_FOLDER = '/Users/tp-01/Documents/Annotation/testone'

# Define your class mappings here
CLASS_MAPPING = {
    "6": "19",
    "1": "13"
}

for txt_file in Path(MAIN_FOLDER).rglob("labels/*.txt"):
    with open(txt_file, "r") as f:
        lines = f.readlines()

    updated_lines = []

    for line in lines:
        parts = line.strip().split()

        if not parts:
            updated_lines.append(line)
            continue

        original_class = parts[0]

        # Change only based on original value
        if original_class in CLASS_MAPPING:
            parts[0] = CLASS_MAPPING[original_class]

        updated_lines.append(" ".join(parts) + "\n")

    with open(txt_file, "w") as f:
        f.writelines(updated_lines)

    print(f"Updated: {txt_file}")

print("Done!")