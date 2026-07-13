import uuid
from datetime import date, datetime
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel
from typing import TYPE_CHECKING
from app.core.models import TimestampMixin

if TYPE_CHECKING:
    from app.modules.sales_invoices.model import SalesInvoice


class CreditNote(TimestampMixin, table=True):
    __tablename__ = "credit_notes"  # pyright: ignore

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    invoice_id: str = Field(foreign_key="sales_invoices.id", index=True)
    credit_note_id: str = Field(unique=True)
    issue_date: date
    pdf_file_path: str | None = None
    zip_file_path: str | None = None
    xml_file_path: str | None = None

    invoice: "SalesInvoice" = Relationship(back_populates="credit_notes")
