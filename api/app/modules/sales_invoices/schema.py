# app/sales_invoices/schemas.py
from datetime import date
from pydantic import BaseModel, computed_field
from .model import CurrencyType, InvoiceStatus


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


# ── Factura: entrada ───────────────────────────────────────────────────────────


class SalesInvoiceCreate(BaseModel):
    period: str
    serie: str
    number: int
    issue_date: date
    customer_ruc: str
    customer_name: str
    currency: CurrencyType = CurrencyType.PEN
    total_amount: float
    local_path: str
    is_advance: bool = False
    status: InvoiceStatus = InvoiceStatus.ACTIVE


# ── Factura: salida (shape que espera el frontend) ────────────────────────────


class SalesInvoiceOut(BaseModel):
    id: str
    invoiceCode: str
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

    # Estado calculado
    # isComplete: bool
    missing: list[str]
