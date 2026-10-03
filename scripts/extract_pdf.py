from pathlib import Path
from pypdf import PdfReader
import unicodedata
import ftfy


PDF_PATH = Path("knowledge/sources/cn/computer-networks-a-systems-approach.pdf")
OUTPUT_PATH = Path("knowledge/processed/cn_raw.txt")


def normalize_text(text: str) -> str:
    """Repair text encoding issues and normalize Unicode."""
    text = ftfy.fix_text(text)
    return unicodedata.normalize("NFKC", text)


def extract_pdf_text():
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(str(PDF_PATH))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = normalize_text(text)

        pages.append(
            f"\n\n===== PAGE {page_number} =====\n\n{text}"
        )

    full_text = "".join(pages)

    OUTPUT_PATH.write_text(full_text, encoding="utf-8")

    print(f"Extracted {len(reader.pages)} pages.")
    print(f"Saved extracted text to: {OUTPUT_PATH}")


if __name__ == "__main__":
    extract_pdf_text()