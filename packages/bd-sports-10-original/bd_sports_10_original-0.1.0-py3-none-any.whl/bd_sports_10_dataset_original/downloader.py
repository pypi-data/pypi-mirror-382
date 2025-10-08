import requests
from tqdm import tqdm
import time


def download_dataset():
    url = "https://download.scidb.cn/download?fileId=e56587341572a1d8576ff59f6f1d9b62&path=/V3/BD_Sports_10.zip&fileName=BD_Sports_10.zip"

    # Start timing
    start_time = time.time()

    # Stream the response
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    chunk_size = 4 * 1024 * 1024  # 4 MB chunks

    # Setup progress bar
    with open("bd_sports_10_dataset_original.zip", "wb") as f, tqdm(
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
        desc="Downloading",
        ncols=100
    ) as bar:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                bar.update(len(chunk))

    # End timing
    elapsed_time = time.time() - start_time
    print(f"\n✅ Download completed in {elapsed_time:.2f} seconds.")
