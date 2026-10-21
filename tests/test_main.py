from fastapi.testclient import TestClient

from invoice_extraction_api.main import app

client = TestClient(app)


def test_extract() -> None:
    response = client.post(
        "/extract", files={"file": ("invoice.pdf", b"fake", "application/pdf")}
    )
    assert response.status_code == 200
    assert response.json()["vendor_name"] == "Acme Supplies Ltd"
    assert response.json()["line_items"][0]["unit_price"] == "5.00"
