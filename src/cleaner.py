import re

def clean_section(text: str, max_bullets=2, max_len=200):
    """Aggressively compress text into 1–2 short bullets."""

    if not text or text.strip() == "Not found":
        return "Not found"

    # Keep existing bullets
    bullets = [b.strip("- ").strip() for b in text.split("\n") if b.strip().startswith("-")]

    # Prefer bullets that are < max_len
    bullets = [b for b in bullets if len(b) < max_len]

    # If too big, shorten sentences
    short = []
    for b in bullets[:max_bullets]:
        # remove overly long parentheticals, numbers, clutter
        b = re.sub(r"\(.*?\)", "", b)
        b = re.sub(r"\s+", " ", b).strip()
        short.append(b)

    if not short:
        return "Not found"

    # Reconstruct into "- bullet" form
    return "\n".join(f"- {s}" for s in short)
