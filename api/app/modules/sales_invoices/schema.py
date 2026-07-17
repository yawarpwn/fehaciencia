from datetime import date
from pydantic import BaseModel, ConfigDict
from app.core.types import CurrencyType
from app.modules.delivery_notes.schema import DeliveryNoteOut
from app.modules.credit_notes.schema import CreditNoteOut


# ── Documentos ────────────────────────────────────────────────────────────────
class DocumentOut(BaseModel):
    id: str
    document_type: str
    file_name: str
    file_url: str
    thumbnail_url: str | None = None

    class Config:
        from_attributes = True


class SalesInvoiceBase(BaseModel):
    period: str
    serie: str
    document_id: str
    sequential_number: int
    issue_date: date
    customer_ruc: str
    customer_name: str
    currency: CurrencyType = CurrencyType.PEN
    total_amount: float
    is_advance: bool = False
    is_credit: bool = False
    pdf_file_path: str | None = None
    xml_file_path: str
    cdr_file_path: str | None = None
    is_advance: bool = False


class SalesInvoiceCreate(SalesInvoiceBase):
    pass


class SalesInvoiceUpdate(BaseModel):
    period: str | None = None
    serie: str | None = None
    sequential_number: int | None = None
    issue_date: date | None = None
    customer_ruc: str | None = None
    customer_name: str | None = None
    currency: CurrencyType | None = None
    total_amount: float | None = None
    local_path: str | None = None
    is_advance: bool | None = None
    document_id: str | None = None
    is_voided: bool | None = None
    is_agency_shipment: bool | None = None
    # status: InvoiceStatus = InvoiceStatus.INCOMPLETE


class SalesInvoiceOut(BaseModel):
    id: str
    document_id: str
    period: str
    customer_ruc: str
    customer_name: str
    customer_short_name: str
    total_amount: float
    is_advance: bool
    issue_date: date
    # missing: list[str]
    purchase_order: DocumentOut | None
    agency_guides: list[DocumentOut]
    signed_delivery_guides: list[DocumentOut]
    payment_vouchers: list[DocumentOut]
    delivery_notes: list[DeliveryNoteOut]
    credit_notes: list[CreditNoteOut]
    photos: list[DocumentOut]
    model_config = ConfigDict(from_attributes=True)
    pdf_file_url: str | None = None
    xml_file_url: str
    status: str
    missing: list[str]
