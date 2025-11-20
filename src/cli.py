from extract_text import extract_pdf_to_text
from summarizer import summarize_text
from section_extractor import extract_sections
import json

def main():
    pdf_path = "data/raw/file.pdf"
    text_path = "data/extracted/text.txt"

    print("Extracting PDF...")
    extract_pdf_to_text(pdf_path, text_path)

    print("Reading text...")
    text = open(text_path, "r", encoding="utf-8").read()

    print("Generating summary (LLM)...")
    summary = summarize_text(text)

    print("Extracting sections (LLM)...")
    sections = extract_sections(text)

    # save output
    output = {
        "summary": summary,
        "sections": sections
    }

    with open("outputs/json/report.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)

    print("\nDONE — Saved to outputs/json/report.json")

if __name__ == "__main__":
    main()
