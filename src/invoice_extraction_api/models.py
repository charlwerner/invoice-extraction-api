from datetime import date
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, model_validator


class LineItem(BaseModel):
    description: str
    quantity: Decimal
    unit_price: Decimal
    amount: Decimal

class Invoice(BaseModel):
    vendor_name: str
    vendor_address: str | None = None
    invoice_number: str
    invoice_date: date
    due_date: date | None = None
    customer_name: str | None = None
    customer_address: str | None = None
    line_items: list[LineItem]
    subtotal: Decimal | None = None
    tax: Decimal | None = None
    total: Decimal
    currency: str | None = None

    @model_validator(mode="after")
    def subtotal_match(self) -> Self:
        line_amount_sum = Decimal(0)
        for line_item in self.line_items:
            line_amount_sum += line_item.amount
        if self.subtotal is None:
            pass
        elif line_amount_sum != self.subtotal:
            raise ValueError("Line item sum does not equal subtotal")
        return self

    @model_validator(mode="after")
    def check_total(self) -> Self:
        if self.subtotal is None or self.tax is None:
            pass
        elif self.subtotal + self.tax != self.total:
            raise ValueError("Subtotal plus tax does not match total")
        return self

         