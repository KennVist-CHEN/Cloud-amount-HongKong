# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///

"""
Fetch the 2026 daily mean amount of cloud data from the Hong Kong Observatory.

    uv run fetch.py

The raw CSV is saved to data/ and is only fetched if the file does not
already exist.
"""

from pathlib import Path

import requests

URL = "https://data.weather.gov.hk/weatherAPI/cis/csvfile/HKO/2026/daily_HKO_CLD_2026.csv"
FILE = "hko-daily-mean-cloud-2026.csv"

HERE = Path(__file__).parent
DATA = HERE / "data"


def fetch(url, path):
    """Ask for the file once. If it is already in data/, do nothing."""
    if path.exists():
        print(
            f"data/{path.name} is already here "
            f"({path.stat().st_size // 1024} KB). "
            "Delete it to fetch again."
        )
        return path

    DATA.mkdir(exist_ok=True)

    print(f"asking {url}")

    reply = requests.get(
        url,
        timeout=60,
        headers={"User-Agent": "SD5913 PolyU student"},
    )

    reply.raise_for_status()

    path.write_bytes(reply.content)

    print(
        f"saved data/{path.name} "
        f"({path.stat().st_size // 1024} KB). "
        "Now: git add data"
    )

    return path


if __name__ == "__main__":
    fetch(URL, DATA / FILE)
