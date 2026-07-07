# ====== USER INPUT ======

BASE_RTSP = "rtsp://SIPTJ:sipt%40654321@183.82.98.202:1800/Streaming/Channels/"

CHANNELS = [1001,
101,
1101,
1201,
1301,
1401,
1501,
1601,
201,
301,
401,
501,
601,
701,
801,
901

]

# =========================


def generate_rtsp_urls(base_url, channels):
    urls = []
    for ch in channels:
        full_url = f"{base_url}{ch}"
        urls.append(full_url)
    return urls


if __name__ == "__main__":

    print("\n✅ Generated RTSP URLs:\n")

    urls = generate_rtsp_urls(BASE_RTSP, CHANNELS)

    for url in urls:
        print(url)