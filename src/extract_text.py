import pdfplumber
import os

def extract_pdf_to_text(pdf_path: str, out_path: str):
    """
    Extracts text from a PDF using pdfplumber and writes clean text to out_path.
    Very lightweight and data-efficient.
    """
    all_text = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                # Basic cleaning: strip trailing spaces
                clean = text.strip()
                all_text.append(clean)

    final_text = "\n\n".join(all_text)

    # Ensure folder exists
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(final_text)

    return out_path


if __name__ == "__main__":
    # For direct testing
    print("Extracting PDF...")
    extract_pdf_to_text("data/raw/file.pdf", "data/extracted/text.txt")
    print("Done: data/extracted/text.txt created.")
