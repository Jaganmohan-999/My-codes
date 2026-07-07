import json

# Load your JSON data (from file or list)
with open("D:\kafka\device.json.json", "r") as f:
    data = json.load(f)

# If your JSON is line-by-line (JSONL), use this instead:
# data = [json.loads(line) for line in open("data.json")]

unique_branches = {}
result = []

for item in data:
    branch_id = item.get("branch_id")

    # Skip if already processed
    if branch_id in unique_branches:
        continue

    unique_branches[branch_id] = True

    extracted = {
        "branch_id": branch_id,
        "camera_number": item.get("camera_number"),
        "camera_ip": item.get("camera_ip"),
        "username": item.get("username")
    }

    result.append(extracted)

# Print result
print(json.dumps(result, indent=2))

# Optional: save to file
with open("output.json", "w") as f:
    json.dump(result, f, indent=2)