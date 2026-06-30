import uuid
from datetime import UTC, datetime
from enum import Enum
from datetime import date
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel


class CurrencyType(str, Enum):
    PEN = "PEN"
    USD = "USD"


class InvoiceStatus(str, Enum):
    ACTIVE = "ACTIVE"
    VOIDED = "VOIDED"


class AssetType(str, Enum):
    INVOICE_XML = "INVOICE_XML"
    INVOICE_ZIP = "INVOICE_ZIP"
    INVOICE_PDF = "INVOICE_PDF"
    DELIVERY_GUIDE_PDF = "DELIVERY_GUIDE_PDF"
    DELIVERY_GUIDE_XML = "DELIVERY_GUIDE_XML"
    SIGNED_SHIPPING_RECEIPT = "SIGNED_SHIPPING_RECEIPT"
    CARRIER_RECEIPT = "CARRIER_RECEIPT"
    PHOTO = "PHOTO"
    BANK_VOUCHER = "BANK_VOUCHER"
    PURCHASE_ORDER = "PURCHASE_ORDER"
    CREDIT_NOTE_PDF = "CREDIT_NOTE_PDF"
    CREDIT_NOTE_ZIP = "CREDIT_NOTE_ZIP"
    CREDIT_NOTE_XML = "CREDIT_NOTE_XML"


class SalesInvoice(SQLModel, table=True):
    __tablename__: str = "sales_invoices"  # type: ignore

    # Definimos el ID como UUID, por defecto genera uno nuevo automáticamente
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )

    period: str = Field(index=True)  # Ej: "202606"
    serie: str  # "E001" o "F001"
    number: int  # 1768
    issue_date: date  # "2026-06-16"
    customer_ruc: str = Field(index=True)  # RUC: "20453668984"
    customer_name: str  # "COMIN S.A.C."
    currency: CurrencyType  # "PEN" o "USD"
    total_amount: float
    is_credit: int = Field(default=0)  # 0 = Contado, 1 = Crédito
    status: str = Field(default="ACTIVE")  # "ACTIVE" o "VOIDED"
    local_path: str  # "COMPROBANTES/2026/06/VENTAS/E001-1768/"
    cf_synced: int = Field(default=0)  # 0 = No sincronizado, 1 = Sincronizado

    # Relación inversa: Si borras una factura, elimina automáticamente sus documentos adjuntos
    documents: List["SupportingDocument"] = Relationship(
        back_populates="invoice",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class SupportingDocument(SQLModel, table=True):
    __tablename__: str = "supporting_documents"  # type: ignore

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)

    # Llave foránea vinculada al UUID de la tabla de facturas
    invoice_id: str = Field(foreign_key="sales_invoices.id")

    document_type: AssetType  # "XML", "PDF", "DELIVERY_GUIDE", "PHOTO", etc.
    file_name: str  # "E001-1768.xml", "foto_letrero.jpg"

    # Guarda la fecha y hora exacta de la carga en formato ISO/Texto
    uploaded_at: str = Field(
        default_factory=lambda: datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
    )

    # Relación para acceder al objeto factura directamente desde el documento
    invoice: SalesInvoice = Relationship(back_populates="documents")
