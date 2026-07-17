from sqlmodel import Session
import os
from app.core.errors import NotFoundAppError, ValidationAppError
from app.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, STORAGE_PATH
from app.core.types import DocumentType
from app.core.utils.helpers import (
    detect_mime_type,
    generate_unique_filename,
    get_path,
    store_file,
)
from app.core.utils.thumbnails import generate_thumbnail
from app.modules.sales_invoices.repository import SaleInvoiceRepository
from .model import SupportingDocument
from .schema import SupportingDocumentCreate, SupportingDocumentUpdate
from .repository import SupportingDocumentRepository


class SupportingDocumentService:
    def __init__(self, session: Session):
        self.repository = SupportingDocumentRepository(session)
        self.invoice_repo = SaleInvoiceRepository(session)

    def get_all(self) -> list[SupportingDocument]:
        return self.repository.get_all()

    def get_by_id(self, document_id: str) -> SupportingDocument:
        doc = self.repository.get_by_id(document_id)
        if not doc:
            raise NotFoundAppError(
                f"Documento de soporte con id {document_id} no encontrado"
            )
        return doc

    def create(
        self,
        *,
        content: bytes,
        document_type: DocumentType,
        invoice_id: str,
        filename: str | None,
    ) -> SupportingDocument:

        if filename is None:
            raise ValidationAppError("No se pudo obtener el nombre del archivo")

        # recuperamos la factura
        invoice = self.invoice_repo.get_by_id(invoice_id)

        if invoice is None:
            raise NotFoundAppError(f"Factura {invoice_id} no encontrada")

        extension = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

        if extension not in ALLOWED_EXTENSIONS:
            raise ValidationAppError(f"Extensión '{extension}' no permitida")

        # Leer contenido y validar tamaño
        if len(content) > MAX_FILE_SIZE:
            raise ValidationAppError(
                f"Archivo demasiado grande. Máximo permitido: {MAX_FILE_SIZE // (1024 * 1024)} MB",
            )
        if len(content) == 0:
            raise ValidationAppError("El archivo está vacío")

        safe_filename = generate_unique_filename(
            original_name=filename, doc_type=document_type
        )

        mime_type = detect_mime_type(content)

        thumbnail_path = None
        # Generar thumbnail si es imagen
        if mime_type.startswith("image"):
            thumb_image_bytes = generate_thumbnail(
                image_bytes=content,
                suffix=extension,
            )

            thumb_image_name = f"thumbnail_{safe_filename}"

            destination_thumb, relative_path_thumb = get_path(
                invoice.period, invoice.document_id, thumb_image_name
            )

            store_file(
                content=thumb_image_bytes,
                target_dir=destination_thumb,
                target_name=thumb_image_name,
            )

            thumbnail_path = relative_path_thumb

        # guardamos el archivo
        destination, relative_path = get_path(
            invoice.period, invoice.document_id, filename
        )

        store_file(content, destination, filename)

        return self.repository.create(
            SupportingDocument(
                invoice_id=invoice_id,
                document_type=document_type,
                file_name=safe_filename,
                file_path=relative_path,
                thumbnail_path=thumbnail_path,
                mime_type=mime_type,
                file_size=len(content),
            )
        )

    def update(
        self, document_id: str, data: SupportingDocumentUpdate
    ) -> SupportingDocument:
        doc = self.get_by_id(document_id)
        return self.repository.update(doc, data.model_dump(exclude_unset=True))

    def delete(self, document_id: str) -> None:
        doc = self.get_by_id(document_id)
        if doc.file_path:
            path = STORAGE_PATH / doc.file_path
            if path.exists() and path.is_file():
                os.remove(path)
        if doc.thumbnail_path:
            thumb_path = STORAGE_PATH / doc.thumbnail_path
            if thumb_path.exists() and thumb_path.is_file():
                os.remove(thumb_path)
        self.repository.delete(doc)
