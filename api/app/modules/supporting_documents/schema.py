from pydantic import BaseModel
from datetime import datetime
from app.modules.sales_invoices.types import DocumentType


class SupportingDocumentBase(BaseModel):
    invoice_id: str
    document_type: DocumentType
    file_name: str
    file_path: str
    mime_type: str
    file_size: int
    thumbnail_path: str | None = None


class SupportingDocumentCreate(SupportingDocumentBase):
    pass


class SupportingDocumentUpdate(BaseModel):
    invoice_id: str | None = None
    document_type: DocumentType | None = None
    file_name: str | None = None
    file_path: str | None = None
    mime_type: str | None = None
    file_size: int | None = None
    thumbnail_path: str | None = None


class SupportingDocumentOut(BaseModel):
    id: str
    invoice_id: str
    document_type: DocumentType
    file_name: str
    file_path: str
    mime_type: str
    file_size: int
    thumbnail_path: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
