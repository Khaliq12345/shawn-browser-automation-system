import os

# PROXY configs
PROXIES = {
    "us": "10000",
    "sg": "10000",
    "ca": "20000",
    "gb": "30000",
    "au": "30000",
    "nz": "39000",
}

LANGUAGUES = ["en"]

# Write down the output files
def save_file(file_path: str, content: str):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path
