from pydantic import BaseModel
from datetime import date, datetime

from app.modules.sales_invoices.model import SalesInvoice
from app.modules.sales_invoices.schema import SalesInvoiceOut


class DeliveryNoteBase(BaseModel):
    invoice_id: str
    delivery_note_id: str
    is_agency_shipment: bool = False
    issue_date: date
    pdf_file_path: str
    zip_file_path: str
    xml_file_path: str | None = None


class DeliveryNoteCreate(DeliveryNoteBase):
    pass


class DeliveryNoteUpdate(BaseModel):
    invoice_id: str | None = None
    delivery_note_id: str | None = None
    is_agency_shipment: bool | None = None
    issue_date: date | None = None
    pdf_file_path: str | None = None
    zip_file_path: str | None = None
    xml_file_path: str | None = None


class DeliveryNoteOut(BaseModel):
    id: str
    document_id: str
    is_agency_shipment: bool
    issue_date: date
    pdf_file_path: str | None = None
    zip_file_path: str | None = None
    xml_file_path: str | None = None
    sale_invoices: list[SalesInvoice]
    # created_at: datetime
    # updated_at: datetime | None = None

    class Config:
        from_attributes = True
