import os
import json
from utils import load_cache, save_cache
from cleaner import clean_section

JSON_KEYS = [
    "definitions",
    "obligations",
    "responsibilities",
    "eligibility",
    "payments",
    "penalties",
    "record_keeping"
]

def extract_sections(text: str):
    """
    FINAL VERSION:
    - Uses cached Claude extraction
    - Cleans it offline
    - Produces small, perfect bullets
    - Zero Groq calls
    """

    # 1) USE CACHE IF EXISTS
    cached = load_cache("sections")
    if cached:
        print("Using cached sections.json")
        return cached

    # 2) LOAD CLAUDE'S HIGH-QUALITY EXTRACTION
    try:
        with open("cache/sections_claude.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise Exception("ERROR: sections_claude.json missing. Please add Claude output there.")

    # 3) CLEAN EACH SECTION (SHORT BULLETS)
    result = {}
    for key in JSON_KEYS:
        result[key] = clean_section(data.get(key, "Not found"))

    # 4) SAVE RESULT
    save_cache("sections", result)
    return result


# MAIN
if __name__ == "__main__":
    print("Creating cleaned section extraction...")

    with open("data/extracted/text.txt", "r", encoding="utf-8") as f:
        text = f.read()

    result = extract_sections(text)

    print("\n=== FINAL CLEANED SECTIONS ===\n")
    print(json.dumps(result, indent=4))

    print("\nSaved to cache/sections.json\n")
