from fastapi.testclient import TestClient

from invoice_extraction_api.main import MAX_FILE_SIZE, app

client = TestClient(app)


def test_extract() -> None:
    response = client.post(
        "/extract", files={"file": ("invoice.pdf", b"fake", "application/pdf")}
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
