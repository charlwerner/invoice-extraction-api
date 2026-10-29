from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, UploadFile

from invoice_extraction_api.models import Invoice
from invoice_extraction_api.pdf_text import pdf_to_text


def extract_invoice(text: str) -> Invoice:
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


def get_extractor() -> Callable[[str], Invoice]:
    return extract_invoice


app = FastAPI()

MAX_FILE_SIZE = 2 * 1024 * 1024


@app.post("/extract")
async def extract(
    file: UploadFile,
    extractor: Annotated[Callable[[str], Invoice], Depends(get_extractor)],
) -> Invoice:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=415, detail="Only PDF files allowed")
    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="File is empty")
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File is too large")
    try:
        text = pdf_to_text(contents)
    except ValueError as err:
        raise HTTPException(status_code=400, detail="File is not a valid PDF") from err
    if text.strip() == "":
        raise HTTPException(status_code=422, detail="PDF contains no text")
    return extractor(text)
