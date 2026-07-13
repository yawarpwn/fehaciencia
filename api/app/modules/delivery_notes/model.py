import uuid
from datetime import date, datetime
from sqlmodel import Field, Relationship, SQLModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.sales_invoices.model import SalesInvoice


class DeliveryNoteReference(SQLModel, table=True):
    __tablename__ = "delivery_note_references"  # pyright: ignore

    delivery_note_id: str = Field(
        foreign_key="delivery_notes.id",
        primary_key=True,
    )

    invoice_id: str = Field(
        foreign_key="sales_invoices.id",
        primary_key=True,
    )


class DeliveryNote(SQLModel, table=True):
    __tablename__ = "delivery_notes"  # pyright: ignore

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    document_id: str = Field(unique=True)
    is_agency_shipment: bool = Field(default=False)
    issue_date: date
    pdf_file_path: str | None = None
    zip_file_path: str | None = None
    xml_file_path: str | None = None
    sales_invoices: list["SalesInvoice"] = Relationship(
        back_populates="delivery_notes", link_model=DeliveryNoteReference
    )
