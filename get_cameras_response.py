import os
import json
import requests

# ============================================================
# CONFIGURATION
# ============================================================

DEVICE_ID = "6a57831dd1d942a8220cbc8a"

LOCATION_IDS = [
"27229bcb-f0e5-4dce-994c-5ed12a15f710",
"e66fa24b-7fa6-48ab-8dbc-1b93b2465799",
"3d0fd243-bc6f-4f00-b0b1-5d349f3a1042",
"87b69166-2060-483c-a1cb-0b942263c271",
"0fdf3bb2-6972-4bc3-91a7-a6036ed20353",
"9c2e1fbe-5ccb-44dd-905e-ee4bcd9ff253",
"962b72ea-e236-490c-ac91-a4b682772940",
"a831d981-45fe-4f41-838c-d213ac90c749",
"50ea8a42-8c37-4372-a830-76ef2b269867",
"a85e303e-9435-4d06-b09b-8e6b663bbf60",
"f6f6e452-6640-4433-b751-ff92b45db9a0",
"d3c71c79-03dd-4d42-a17b-12bbe83e94ad",
"fa2a786a-2937-480b-8bef-0c293ff4e716",
"2d112f25-19ba-4f63-a6f9-70d8e44d6b62"
]

OUTPUT_FOLDER = "/Users/tp-01/Documents/VS_outputs/Get_camera_jsons"

# Paste your CURRENT token here
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWQiOiI1MThiYWYxYi0zOGJkLTQzMTUtOGRiOC0zNDMwMGI5NTQzNWUiLCJjb21wYW55SWQiOiIzMTQzZDc1YS1iOTY2LTQ5MDktYjgyZS0yNmUxOTcyZjViZjEiLCJpYXQiOjE3ODY2ODc2MzEsImV4cCI6MTc4Njc3NDAzMX0.mS0TnVGwtUpW-FmunT7olZ8rOY_lUX7bzrSlIupZ3wo"

# ============================================================
# API
# ============================================================

BASE_URL = (
    "https://prod.tpsmartsol.com/"
    "surveillance/api/v1/cameras/getByDevice"
)

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def get_camera_data(device_id, location_id):

    url = f"{BASE_URL}/{device_id}/{location_id}"

    headers = {
        "accept": "application/json, text/plain, */*",
        "origin": "https://cbt.tpsmartsol.com",
        "referer": "https://cbt.tpsmartsol.com/",
        "web": "true",
        "x-tpsmartsol-token": TOKEN,
    }

    print("\nRequesting:")
    print(url)

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        print("Status:", response.status_code)

        if response.status_code != 200:
            print("❌ Request failed")
            print("Response:", response.text[:500])
            return None

        return response.json()

    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return None

    except requests.exceptions.RequestException as e:
        print("❌ Request error:", e)
        return None

    except json.JSONDecodeError:
        print("❌ Response is not valid JSON")
        print(response.text[:500])
        return None


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("CAMERA API DATA FETCH")
    print("=" * 60)

    print(f"Device ID    : {DEVICE_ID}")
    print(f"Locations    : {len(LOCATION_IDS)}")
    print(f"Output folder: {OUTPUT_FOLDER}")

    success_count = 0
    failed_count = 0

    for index, location_id in enumerate(LOCATION_IDS, start=1):

        print("\n" + "-" * 60)
        print(f"Location {index}/{len(LOCATION_IDS)}")
        print(f"Location ID: {location_id}")

        data = get_camera_data(
            DEVICE_ID,
            location_id
        )

        if data is None:
            failed_count += 1
            continue

        # Save each location response separately
        output_file = os.path.join(
            OUTPUT_FOLDER,
            f"{location_id}.json"
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

        print("✅ Saved:", output_file)

        success_count += 1

    print("\n" + "=" * 60)
    print("COMPLETED")
    print("=" * 60)

    print(f"Successful : {success_count}")
    print(f"Failed     : {failed_count}")
    print(f"Total      : {len(LOCATION_IDS)}")
    print(f"Output     : {OUTPUT_FOLDER}")


if __name__ == "__main__":
    main()