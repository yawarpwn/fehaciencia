from sqlmodel import Session
import shutil

from app.core.errors import (
    NotFoundAppError,
    ResourseAlreadyExistsAppError,
    ValidationAppError,
)
from app.core.utils import (
    detect_mime_type,
    generate_unique_filename,
    store_file,
    generate_thumbnail,
)
from app.core.utils.helpers import get_path, parse_zip_invoice
from .model import SalesInvoice
from .schema import SalesInvoiceCreate, SalesInvoiceOut, SalesInvoiceUpdate
from app.core.serializer import serialize_invoice, serialize_document
from .repository import SaleInvoiceRepository
from app.core.types import DocumentType
from app.modules.supporting_documents.model import SupportingDocument
from app.config import (
    ALLOWED_EXTENSIONS,
    STORAGE_PATH,
    MAX_FILE_SIZE,
)


class SaleInvoiceService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = SaleInvoiceRepository(session)

    def _get_entity_by_id(self, id: str) -> SalesInvoice:
        invoice = self.repository.get_by_id(id)
        if invoice is None:
            raise NotFoundAppError(f"Factura con id {id} no encontrada")
        return invoice

    def get_filtered_and_serialized(
        self,
        q: str | None = None,
        period: str | None = None,
        status: str | None = None,
    ) -> list[SalesInvoiceOut]:
        invoices = self.repository.get_all(q=q, period=period)
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
        return self.repository.get_distinct_periods()

    def get_by_id(self, id: str) -> SalesInvoiceOut:
        invoice = self._get_entity_by_id(id)
        return serialize_invoice(invoice)

    def get_by_document_id(self, document_id: str) -> SalesInvoiceOut:
        invoice = self.repository.get_by_document_id(document_id)
        if invoice is None:
            raise NotFoundAppError(f"Factura {document_id} no encontrada")
        return serialize_invoice(invoice)

    def find_by_serie_and_number(self, document_id: str) -> SalesInvoiceOut:
        invoice = self.repository.get_by_document_id(document_id)
        if invoice is None:
            raise NotFoundAppError(f"Factura {document_id} no encontrada")
        return serialize_invoice(invoice)

    def create(self, data: SalesInvoiceCreate) -> SalesInvoiceOut:
        exists = self.repository.get_by_document_id(data.document_id)
        if exists is not None:
            raise ResourseAlreadyExistsAppError(f"Factura {data.document_id} ya existe")

        invoice = SalesInvoice(**data.model_dump())
        created_invoice = self.repository.create(invoice)
        return serialize_invoice(created_invoice)

    def create_from_zip(self, content: bytes):
        parsed = parse_zip_invoice(content)

        if parsed is None:
            raise ValidationAppError("Error procesando zip de factura")

        iv = parsed.data

        # Validar si la factura ya existe
        if self.repository.get_by_document_id(iv.document_id) is not None:
            raise ResourseAlreadyExistsAppError(f"Factura {iv.document_id} ya existe")

        destination, file_path = get_path(iv.period, iv.document_id, parsed.xml_name)

        # Guarda en disco
        store_file(parsed.xml_bytes, destination, parsed.xml_name)

        return self.create(
            SalesInvoiceCreate(
                document_id=iv.document_id,
                period=iv.period,
                xml_file_path=file_path,
                issue_date=iv.issue_date,
                serie=iv.serie,
                customer_name=iv.customer_name,
                customer_ruc=iv.customer_ruc,
                sequential_number=iv.sequential_number,
                total_amount=iv.total_amount,
            )
        )

    def insert_pdf(self, invoice_id: str, content: bytes, filename: str | None):

        if filename is None:
            raise ValidationAppError("No se pudo obtener el nombre del archivo")

        invoice = self.repository.get_by_id(invoice_id)

        if invoice is None:
            raise NotFoundAppError(f"Factura {invoice_id} no encontrada")

        destination, file_path = get_path(invoice.period, invoice.document_id, filename)
        store_file(content, destination, filename)

        self.repository.update(invoice, data_dict={"pdf_file_path": file_path})

    def update(self, id: str, data: SalesInvoiceUpdate) -> SalesInvoiceOut:
        invoice = self._get_entity_by_id(id)

        # Validar si el invoice_id cambia y ya existe otra con el nuevo id
        # if data.invoice_id is not None and data.invoice_id != invoice.invoice_id:
        #     exists = self.repository.get_by_invoice_id(data.invoice_id)
        #     if exists is not None:
        #         raise ConflictAppError(
        #             f"Ya existe otra factura con el ID {data.invoice_id}"
        #         )

        updated_invoice = self.repository.update(
            invoice, data.model_dump(exclude_unset=True)
        )
        return serialize_invoice(updated_invoice)

    def update_by_document_id(
        self, document_id: str, data: SalesInvoiceUpdate
    ) -> SalesInvoiceOut:
        invoice = self.repository.get_by_document_id(document_id=document_id)

        if invoice is None:
            raise NotFoundAppError(f"Factura con id {document_id} no encontrada")

        updated_invoice = self.repository.update(
            invoice, data.model_dump(exclude_unset=True)
        )
        return serialize_invoice(updated_invoice)

    def delete_sale_invoice(self, id: str) -> None:
        invoice = self._get_entity_by_id(id)

        # Borrar archivos físicos del almacenamiento
        # if invoice.local_path:
        #     invoice_path = STORAGE_PATH / invoice.local_path
        #     if invoice_path.exists() and invoice_path.is_dir():
        #         shutil.rmtree(invoice_path)

        # Borrar de la base de datos (cascada se encarga de SupportingDocuments)
        self.repository.delete(invoice)

    async def upload_file(
        self,
        invoice_id: str,
        document_type: DocumentType,
        content: bytes,
        filename: str,
    ):
        # 1. Validar Extensión
        original_name = filename or "archivo_sin_nombre"
        extension = (
            "." + original_name.rsplit(".", 1)[-1].lower()
            if "." in original_name
            else ""
        )

        # Recuperar sale_invoice (entidad)
        invoice = self._get_entity_by_id(invoice_id)
        if extension not in ALLOWED_EXTENSIONS:
            raise ValidationAppError(f"Extensión '{extension}' no permitida")

        # Leer contenido y validar tamaño
        if len(content) > MAX_FILE_SIZE:
            raise ValidationAppError(
                f"Archivo demasiado grande. Máximo permitido: {MAX_FILE_SIZE // (1024 * 1024)} MB",
            )
        if len(content) == 0:
            raise ValidationAppError("El archivo está vacío")

        # Generar nombre único
        safe_filename = generate_unique_filename(
            original_name=original_name, doc_type=document_type
        )

        relative_path = f"{invoice.period}/VENTAS/{invoice.document_id}"
        destination = STORAGE_PATH / relative_path

        if document_type == DocumentType.INVOICE_PDF:
            pass

        mime_type = detect_mime_type(content)

        thumbnail_path = None
        # Generar thumbnail si es imagen
        if mime_type.startswith("image"):
            thumb_image_bytes = generate_thumbnail(
                image_bytes=content,
                suffix=extension,
            )
            thumb_image_name = f"thumbnail_{safe_filename}"
            thumbnail_path = f"{relative_path}/{thumb_image_name}"
            store_file(
                content=thumb_image_bytes,
                target_dir=destination,
                target_name=thumb_image_name,
            )

        # Guardar en Disco
        store_file(
            content=content,
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
            file_size=len(content),
            thumbnail_path=thumbnail_path,
        )
        created_document = self.repository.add_document(document)

        return serialize_document(created_document)
