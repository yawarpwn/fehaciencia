from pydantic import BaseModel
from datetime import date, datetime


class CreditNoteBase(BaseModel):
    invoice_id: str
    credit_note_id: str
    issue_date: date
    pdf_file_url: str | None = None
    zip_file_url: str | None = None
    xml_file_url: str | None = None


class CreditNoteCreate(CreditNoteBase):
    pass


class CreditNoteUpdate(BaseModel):
    invoice_id: str | None = None
    credit_note_id: str | None = None
    issue_date: date | None = None
    pdf_file_url: str | None = None
    zip_file_url: str | None = None
    xml_file_url: str | None = None


class CreditNoteOut(BaseModel):
    id: str
    invoice_id: str
    credit_note_id: str
    issue_date: date
    zip_file_url: str | None = None
    pdf_file_url: str | None = None
    xml_file_url: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
