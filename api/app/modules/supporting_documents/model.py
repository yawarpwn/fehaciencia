import uuid
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel
from typing import TYPE_CHECKING
from app.core.types import DocumentType
from app.core.models import TimestampMixin

if TYPE_CHECKING:
    from app.modules.sales_invoices.model import SalesInvoice


class SupportingDocument(TimestampMixin, table=True):
    __tablename__ = "supporting_documents"  # pyright: ignore

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    invoice_id: str = Field(foreign_key="sales_invoices.id", index=True)
    document_type: DocumentType
    file_name: str  # "foto_letrero.jpg"
    file_path: str  # ruta relativa dentro de DATA_PATH/storage
    mime_type: str  # "image/jpeg", "application/pdf"
    file_size: int  # bytes
    thumbnail_path: str | None = None

    invoice: Optional["SalesInvoice"] = Relationship(back_populates="documents")
