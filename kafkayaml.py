import sys

def generate_yaml(base_rtsp, channels,
                  edge_id="edge-dev-01",
                  broker="kafka:9092",
                  topic="frames.raw",
                  fps=5,
                  width=640,
                  height=480,
                  model="yolov8_b16"):

    yaml_output = []

    # Header
    yaml_output.append(f"edge_id: {edge_id}\n")
    yaml_output.append("kafka:")
    yaml_output.append(f"  broker: {broker}")
    yaml_output.append(f"  topic: {topic}\n")

    yaml_output.append("defaults:")
    yaml_output.append(f"  fps: {fps}")
    yaml_output.append(f"  width: {width}")
    yaml_output.append(f"  height: {height}")
    yaml_output.append(f"  model: {model}\n")

    yaml_output.append("cameras:")

    # Cameras section
    for ch in channels:
        rtsp_url = base_rtsp.format(ch)

        yaml_output.append(f"  - camera_id: cam{ch}")
        yaml_output.append(f"    rtsp: {rtsp_url}")
        yaml_output.append("    video: /app/media/retail_store.mp4")
        yaml_output.append("    source: rtsp\n")

    return "\n".join(yaml_output)


if __name__ == "__main__":

    # Example input
    base_rtsp = "rtsp://SIKTPJ:ktpjew@5202@183.82.99.50:1800/Streaming/Channels/{}"

    channels = [
    101,
    201,
    301,
    401
    ]

    yaml_config = generate_yaml(base_rtsp, channels)

    print(yaml_config)
