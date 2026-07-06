from fastapi import HTTPException, UploadFile
from sqlmodel import Session, select, or_
from sqlalchemy.orm import selectinload
from .types import DocumentType

from app.core.errors import NotFoundAppError, ValidationAppError
from app.core.utils import (
    detect_mime_type,
    generate_unique_filename,
    store_file,
    generate_thumbnail,
)
from .model import SalesInvoice, SupportingDocument
from .schema import SalesInvoiceCreate, SalesInvoiceOut
from .serializer import serialize_invoice, serialize_document
from app.config import (
    ALLOWED_EXTENSIONS,
    STORAGE_PATH,
    MAX_FILE_SIZE,
)


class SaleInvoiceService:
    def __init__(self, session: Session):
        self.session = session

    def _base_query(self, q: str | None = None):
        query = select(SalesInvoice).options(selectinload(SalesInvoice.documents))
        if q:
            search_pattern = f"%{q}%"
            query = query.where(
                or_(
                    SalesInvoice.invoice_id.like(search_pattern),
                    SalesInvoice.customer_ruc.like(search_pattern),
                    SalesInvoice.customer_name.like(search_pattern),
                )
            )
        return query.order_by(
            SalesInvoice.period.desc(), SalesInvoice.sequential_number.desc()
        )

    def get_filtered_and_serialized(
        self,
        q: str | None = None,
        period: str | None = None,
        status: str | None = None,
    ) -> list[SalesInvoiceOut]:
        query = self._base_query(q)
        if period:
            query = query.where(SalesInvoice.period == period)

        invoices = self.session.exec(query).all()
        serialized = [serialize_invoice(inv) for inv in invoices]

        if status:
            serialized = [inv for inv in serialized if inv.status == status]

        return serialized

    def get_all(
        self,
        q: str | None = None,
        period: str | None = None,
        status: str | None = None,
    ) -> list[SalesInvoiceOut]:
        return self.get_filtered_and_serialized(q=q, period=period, status=status)

    def get_paginated(
        self,
        page: int,
        limit: int,
        q: str | None = None,
        period: str | None = None,
        status: str | None = None,
    ) -> tuple[list[SalesInvoiceOut], int]:
        all_matches = self.get_filtered_and_serialized(
            q=q, period=period, status=status
        )
        total = len(all_matches)

        offset = (page - 1) * limit
        paginated_slice = all_matches[offset : offset + limit]

        return paginated_slice, total

    def get_distinct_periods(self) -> list[str]:
        periods = self.session.exec(
            select(SalesInvoice.period).distinct().order_by(SalesInvoice.period.desc())
        ).all()
        return list(periods)

    def get_by_id(self, invoice_id: str) -> SalesInvoiceOut:
        invoice = self.session.exec(
            self._base_query().where(SalesInvoice.id == invoice_id)
        ).first()

        if invoice is None:
            raise NotFoundAppError(f"Facuta con id {invoice_id} no encontrada")

        return serialize_invoice(invoice)

    def get_by_invoice_id(self, invoice_id: str) -> SalesInvoiceOut:
        invoice = self.session.exec(
            self._base_query().where(SalesInvoice.invoice_id == invoice_id)
        ).first()

        if invoice is None:
            raise NotFoundAppError(f"Facuta {invoice_id} no encontrada")

        return serialize_invoice(invoice)

    def find_by_serie_and_number(self, serie: str, number: int):
        stqm = select(SalesInvoice).where(
            SalesInvoice.serie == serie, SalesInvoice.sequential_number == number
        )
        invoice = self.session.exec(stqm).first()

        if invoice is None:
            return None

        return serialize_invoice(invoice)

    def create(self, data: SalesInvoiceCreate) -> SalesInvoiceOut:
        invoice = SalesInvoice(**data.model_dump())
        self.session.add(invoice)
        self.session.commit()
        self.session.refresh(invoice)
        return serialize_invoice(invoice)

    async def upload_file(
        self, invoice_id: str, document_type: DocumentType, file: UploadFile
    ):
        # 1. Validar Extension
        original_name = file.filename or "archivo_sin_nombre"
        extension = (
            "." + original_name.rsplit(".", 1)[-1].lower()
            if "." in original_name
            else ""
        )

        # Recuperar sale_invoice
        invoice = self.get_by_id(invoice_id)

        if extension not in ALLOWED_EXTENSIONS:
            raise ValidationAppError(f"Extensión '{extension} no permitida'")

        #  Leer contenido y validar tamaño
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise ValidationAppError(
                f"Archivo demasiado grande: Máximo permitido: {MAX_FILE_SIZE // (1024 * 1024)}",
            )
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="El archivo esta vacío")

        # Generar nombre único
        safe_filename = generate_unique_filename(
            original_name=original_name, doc_type=document_type
        )

        relative_path = f"{invoice.period}/VENTAS/{invoice.invoiceId}"
        destination = STORAGE_PATH / relative_path

        mime_type = detect_mime_type(contents)

        thumbnail_path = None
        # genera thumbnail si es imagen
        if mime_type.startswith("image"):
            thumb_image_bytes = generate_thumbnail(
                image_bytes=contents,
                suffix=extension,
            )
            thumb_image_image = f"thumbnail_{safe_filename}"
            thumbnail_path = f"{relative_path}/{thumb_image_image}"
            store_file(
                source=thumb_image_bytes,
                target_dir=destination,
                target_name=thumb_image_image,
            )

        # Guardar Disco
        store_file(
            source=contents,
            target_dir=destination,
            target_name=safe_filename,
        )

        # Guardar en BD
        document = SupportingDocument(
            invoice_id=invoice_id,
            document_type=document_type,
            file_name=original_name,
            file_path=f"{relative_path}/{safe_filename}",
            mime_type=mime_type,
            file_size=len(contents),
            thumbnail_path=thumbnail_path,
        )
        self.session.add(document)
        self.session.commit()
        self.session.refresh(document)

        return serialize_document(document)
