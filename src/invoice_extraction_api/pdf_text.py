from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError


def pdf_to_text(contents: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(contents))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except PdfReadError as err:
        raise ValueError("File is not a valid PDF") from err
    return text
