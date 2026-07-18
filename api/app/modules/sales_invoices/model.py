import uuid
from datetime import date
from sqlmodel import Field, Relationship
from sqlalchemy import event
from typing import TYPE_CHECKING
from app.core.types import CurrencyType
from app.core.models import TimestampMixin
from app.core.utils import utc_now

from app.modules.supporting_documents.model import SupportingDocument

from app.modules.delivery_notes.model import DeliveryNoteReference

if TYPE_CHECKING:
    from app.modules.credit_notes.model import CreditNote
    from app.modules.delivery_notes.model import DeliveryNote


class SalesInvoice(TimestampMixin, table=True):
    __tablename__ = "sales_invoices"  # pyright: ignore

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )
    period: str = Field(index=True)  # "202606"
    serie: str  # "E001"
    document_id: str = Field(index=True, unique=True)
    sequential_number: int  # 1768
    issue_date: date
    customer_ruc: str = Field(index=True)
    customer_name: str
    currency: CurrencyType
    total_amount: float
    is_advance: bool = Field(default=False)
    is_credit: bool = Field(default=False)
    pdf_file_path: str | None = None
    xml_file_path: str
    cdr_file_path: str | None = None
    credit_notes: list["CreditNote"] = Relationship(back_populates="invoice")

    delivery_notes: list["DeliveryNote"] = Relationship(
        back_populates="sales_invoices", link_model=DeliveryNoteReference
    )

    documents: list["SupportingDocument"] = Relationship(
        back_populates="invoice",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "order_by": "SupportingDocument.created_at",
        },
    )


@event.listens_for(SalesInvoice, "before_update", propagate=True)
def _update_invoice_timestamp(mapper, connection, target):
    target.updated_at = utc_now()
