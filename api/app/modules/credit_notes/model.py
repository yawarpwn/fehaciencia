import uuid
from datetime import date
from sqlmodel import Field, Relationship
from typing import TYPE_CHECKING
from app.core.models import TimestampMixin

if TYPE_CHECKING:
    from app.modules.sales_invoices.model import SalesInvoice


class CreditNote(TimestampMixin, table=True):
    __tablename__ = "credit_notes"  # pyright: ignore

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    invoice_id: str = Field(foreign_key="sales_invoices.id", index=True)
    document_id: str = Field(unique=True)
    issue_date: date
    pdf_file_path: str | None = None
    xml_file_path: str
    cdr_file_path: str | None = None
    # discrepancy_reference_id: str
    discrepancy_response_code: str
    discrepancy_description: str

    invoice: "SalesInvoice" = Relationship(back_populates="credit_notes")
