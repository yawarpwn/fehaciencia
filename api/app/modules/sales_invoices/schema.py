# app/sales_invoices/schemas.py
from datetime import date
from pydantic import BaseModel, computed_field
from .model import CurrencyType
from .document_rules import InvoiceStatus


# ── Documentos ────────────────────────────────────────────────────────────────


class DocumentOut(BaseModel):
    id: str
    documentType: str
    fileName: str
    uploadedAt: str
    fileUrl: str
    thumbnailUrl: str | None = None

    class Config:
        from_attributes = True


class SalesInvoiceBase(BaseModel):
    period: str
    serie: str
    sequential_number: int
    issue_date: date
    customer_ruc: str
    customer_name: str
    currency: CurrencyType = CurrencyType.PEN
    total_amount: float
    local_path: str
    is_advance: bool = False
    invoice_id: str
    is_voided: bool = False
    is_agency_shipment: bool = False


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
    invoice_id: str | None = None
    is_voided: bool | None = None
    is_agency_shipment: bool | None = None
    # status: InvoiceStatus = InvoiceStatus.INCOMPLETE


# ── Factura: salida (shape que espera el frontend) ────────────────────────────


class SalesInvoiceOut(BaseModel):
    id: str
    invoiceId: str
    period: str
    status: str
    customerRuc: str
    customerName: str
    customerShortName: str
    totalAmount: float
    isAdvance: bool
    isAgencyShipment: bool

    # Documentos agrupados
    purchaseOrder: DocumentOut | None
    pdfFile: DocumentOut | None
    deliveryGuides: list[DocumentOut]
    agencyGuides: list[DocumentOut]
    signedDeliveryGuides: list[DocumentOut]
    photos: list[DocumentOut]
    vouchers: list[DocumentOut]
    creditNote: DocumentOut | None
    issueDate: str

    # Estado calculado
    # isComplete: bool
    missing: list[str]
