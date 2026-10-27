from pathlib import Path

import pytest

from invoice_extraction_api.pdf_text import pdf_to_text


def test_pdf_contains() -> None:
    contents = Path("tests/fixtures/sample_invoice.pdf").read_bytes()
    text = pdf_to_text(contents)
    assert "Acme Supplies Ltd" in text


def test_rejects_non_pdf_bytes() -> None:
    with pytest.raises(ValueError, match="File is not a valid PDF"):
        pdf_to_text(b"not a pdf")
