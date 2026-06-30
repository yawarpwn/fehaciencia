from pydantic import BaseModel
from datetime import date

from .model import SupportingDocument


class SupportingDocumentResponse(BaseModel):
    id: str
    document_type: str
    file_name: str
    uploaded_at: str

    class Config:
        from_attributes = True


class SalesInvoiceBase(BaseModel):
    period: str
    serie: str
    number: int
    issue_date: date
    customer_ruc: str
    customer_name: str
    currency: str
    total_amount: float
    local_path: str
    status: str = "ACTIVE"

    class Config:
        from_attributes = True


class CreateSalesInvoice(SalesInvoiceBase):
    pass


class SalesInvoiceResponse(SalesInvoiceBase):
    documents: list[SupportingDocumentResponse] = []
    id: str
