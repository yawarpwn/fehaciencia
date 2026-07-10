# app/sales_invoices/models.py
import uuid
from datetime import UTC, datetime, date
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import event
from .types import CurrencyType, DocumentType


def utc_now() -> datetime:
    return datetime.now(UTC)


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime | None = Field(default=None)


class SalesInvoice(TimestampMixin, table=True):
    __tablename__ = "sales_invoices"  # pyright: ignore

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )
    period: str = Field(index=True)  # "202606"
    serie: str  # "E001"
    invoice_id: str = Field(index=True, unique=True)
    sequential_number: int  # 1768
    issue_date: date
    customer_ruc: str = Field(index=True)
    customer_name: str
    currency: CurrencyType = Field(default=CurrencyType.PEN)
    total_amount: float
    is_advance: bool = Field(default=False)
    is_voided: bool = Field(default=False)
    is_credit: bool = Field(default=False)
    local_path: str  # "202606/VENTAS/E001-1768" — carpeta base en disco
    pdf_file_path: str | None
    zip_file_path: str | None
    xml_file_path: str | None

    is_agency_shipment: bool = Field(default=False)

    documents: List["SupportingDocument"] = Relationship(
        back_populates="invoice",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "order_by": "SupportingDocument.created_at",
        },
    )


@event.listens_for(SalesInvoice, "before_update", propagate=True)
def _update_invoice_timestamp(mapper, connection, target):
    target.updated_at = utc_now()


class SupportingDocument(TimestampMixin, table=True):
    __tablename__ = "supporting_documents"  # pyright: ignore

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    invoice_id: str = Field(foreign_key="sales_invoices.id", index=True)
    document_type: DocumentType
    file_name: str  # "foto_letrero.jpg"
    file_path: str  # ruta relativa dentro de DATA_PATH/storage
    # ej: "202606/VENTAS/E001-1768/foto_letrero.jpg"
    mime_type: str  # "image/jpeg", "application/pdf"
    file_size: int  # bytes
    thumbnail_path: str | None

    invoice: Optional[SalesInvoice] = Relationship(back_populates="documents")


class CreditNote(TimestampMixin, table=True):
    __tablename__ = "credit_notes"  # pyright: ignore

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    invoice_id: str = Field(foreign_key="sales_invoices.id", index=True)
    credit_note_id: str = Field(unique=True)
    issue_date: date
    pdf_file_path: str
    zip_file_path: str
    xml_file_path: str | None


class DeliveryNote(TimestampMixin, table=True):
    __tablename__ = "delivery_notes"  # pyright: ignore

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    invoice_id: str = Field(foreign_key="sales_invoices.id", index=True)
    delivery_note_id: str = Field(unique=True)
    is_agency_shipment: bool = Field(default=False)
    issue_date: date
    pdf_file_path: str
    zip_file_path: str
    xml_file_path: str | None
