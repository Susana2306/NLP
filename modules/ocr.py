import re
import fitz
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text(image: Image.Image, lang: str = "spa") -> str:
    """Run Tesseract OCR on a PIL image and return the raw text."""
    try:
        return pytesseract.image_to_string(image, lang=lang)
    except Exception as exc:
        raise RuntimeError(f"Error en OCR: {exc}") from exc


def extract_text_from_pdf(pdf_bytes: bytes, lang: str = "spa") -> tuple[str, int]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages_text: list[str] = []

    for page in doc:
        text = page.get_text().strip()
        if text:
            pages_text.append(text)
        else:
            pix = page.get_pixmap(dpi=200)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            pages_text.append(extract_text(img, lang=lang))

    return "\n\n".join(pages_text), len(doc)


def clean_text(text: str) -> str:
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"[^\w\sáéíóúñüÁÉÍÓÚÑÜ.,;:¿?¡!()\-]", "", text)
    return text.strip()
