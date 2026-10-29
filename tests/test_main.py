from collections.abc import Callable
from pathlib import Path

from fastapi.testclient import TestClient

from invoice_extraction_api.main import MAX_FILE_SIZE, app, get_extractor
from invoice_extraction_api.models import Invoice

client = TestClient(app)


def fake_extractor_invoice(text: str) -> Invoice:
    return Invoice.model_validate(
        {
            "vendor_name": "Fake Vendor",
            "invoice_number": "INV-1001",
            "invoice_date": "2026-10-01",
            "line_items": [
                {
                    "description": "Printer paper",
                    "quantity": "10",
                    "unit_price": "5.00",
                    "amount": "50.00",
                },
                {
                    "description": "Toner cartridge",
                    "quantity": "2",
                    "unit_price": "35.00",
                    "amount": "70.00",
                },
            ],
            "subtotal": "120.00",
            "tax": "18.00",
            "total": "138.00",
            "currency": "ZAR",
        }
    )


def get_fake_extractor() -> Callable[[str], Invoice]:
    return fake_extractor_invoice


def test_extract() -> None:
    contents = Path("tests/fixtures/sample_invoice.pdf").read_bytes()
    response = client.post(
        "/extract", files={"file": ("invoice.pdf", contents, "application/pdf")}
    )
    assert response.status_code == 200
    assert response.json()["vendor_name"] == "Acme Supplies Ltd"
    assert response.json()["line_items"][0]["unit_price"] == "5.00"


def test_extract_file_type() -> None:
    response = client.post(
        "/extract", files={"file": ("invoice.pdf", b"fake", "image/jpeg")}
    )
    assert response.status_code == 415
    assert response.json()["detail"] == "Only PDF files allowed"


def test_extract_empty() -> None:
    response = client.post(
        "/extract", files={"file": ("invoice.pdf", b"", "application/pdf")}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "File is empty"


def test_extract_size() -> None:
    response = client.post(
        "/extract",
        files={"file": ("invoice.pdf", b"x" * (MAX_FILE_SIZE + 1), "application/pdf")},
    )
    assert response.status_code == 413
    assert response.json()["detail"] == "File is too large"


def test_extract_invalid_pdf() -> None:
    response = client.post(
        "/extract", files={"file": ("invoice.pdf", b"not a pdf", "application/pdf")}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "File is not a valid PDF"


def test_extract_no_text() -> None:
    data = Path("tests/fixtures/blank_invoice.pdf").read_bytes()
    response = client.post(
        "/extract", files={"file": ("blank_invoice.pdf", data, "application/pdf")}
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "PDF contains no text"


def test_extract_override() -> None:
    app.dependency_overrides[get_extractor] = get_fake_extractor
    data = Path("tests/fixtures/sample_invoice.pdf").read_bytes()
    response = client.post(
        "/extract", files={"file": ("sample_invoice.pdf", data, "application/pdf")}
    )
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["vendor_name"] == "Fake Vendor"
