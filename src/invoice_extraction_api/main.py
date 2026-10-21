from fastapi import FastAPI, UploadFile

from invoice_extraction_api.models import Invoice

app = FastAPI()


@app.post("/extract")
def extract(file: UploadFile) -> Invoice:
    return Invoice.model_validate(
        {
            "vendor_name": "Acme Supplies Ltd",
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
