# ====== USER INPUT ======

BASE_RTSP = "rtsp://SIKTPJ:ktpjew@5202@183.82.99.50:1810/Streaming/Channels/"

CHANNELS = [1001,
101,
1101,
1701,
1801,
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