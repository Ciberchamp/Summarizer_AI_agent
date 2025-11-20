import os
import json

def chunk_text(text, max_chars=5000):
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end])
        start = end
    return chunks


# ------- CACHE SYSTEM ------- #

def load_cache(name: str):
    """Loads cache file if exists, else returns None."""
    path = f"cache/{name}.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_cache(name: str, data):
    """Saves cache data to disk."""
    os.makedirs("cache", exist_ok=True)
    path = f"cache/{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
