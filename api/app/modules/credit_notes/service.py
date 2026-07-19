from sqlmodel import Session
import os
from app.core.errors import (
    NotFoundAppError,
    ResourseAlreadyExistsAppError,
    ValidationAppError,
)
from app.config import STORAGE_PATH
from app.core.utils.helpers import get_path, parse_credit_note_zip, store_file
from app.modules.sales_invoices.repository import SaleInvoiceRepository
from .model import CreditNote
from .schema import CreditNoteCreate, CreditNoteUpdate
from .repository import CreditNoteRepository


class CreditNoteService:
    def __init__(self, session: Session):
        self.repository = CreditNoteRepository(session)
        self.sales_invoices_repo = SaleInvoiceRepository(session)

    def get_all(self) -> list[CreditNote]:
        return self.repository.get_all()

    def get_by_id(self, id: str) -> CreditNote:
        cn = self.repository.get_by_id(id)
        if not cn:
            raise NotFoundAppError(f"Nota de crédito con id {id} no encontrada")
        return cn

    def get_by_document_id(self, document_id: str) -> CreditNote:
        cn = self.repository.get_by_document_id(document_id)
        print("cn", cn)
        if cn is None:
            raise NotFoundAppError(f"Nota de crédito {document_id} no encontrada")
        return cn

    def create(self, data: CreditNoteCreate) -> CreditNote:
        cn = CreditNote(**data.model_dump())
        return self.repository.create(cn)

    def insert_pdf(self, id: str, content: bytes, filename: str | None):

        if filename is None:
            raise ValidationAppError("No se pudo obtener el nombre del archivo")

        credit_note = self.get_by_id(id)
        invoice = self.sales_invoices_repo.get_by_id(credit_note.invoice_id)

        if credit_note is None:
            raise NotFoundAppError(f"Nota de crédito {id} no encontrada")

        if invoice is None:
            raise NotFoundAppError(f"Factura {id} no encontrada")

        destination, relative_path = get_path(
            invoice.period, invoice.document_id, filename
        )
        store_file(content, destination, filename)

        self.repository.update(credit_note, data_dict={"pdf_file_path": relative_path})

    def create_from_zip(self, content: bytes):

        parsed = parse_credit_note_zip(content)

        if parsed is None:
            raise ValidationAppError("Error procesando Zip de Nota de Crédito")

        cn = parsed.data
        invoice = self.sales_invoices_repo.get_by_document_id(
            cn.discrepancy_reference_id
        )

        if invoice is None:
            raise NotFoundAppError(f"Factura {cn.document_id} no encontrada")

        # Validar si la nota de crédito ya existe
        if self.repository.get_by_document_id(cn.document_id) is not None:
            raise ResourseAlreadyExistsAppError(
                f"Nota de credito {cn.document_id} ya existe"
            )

        destionation, file_path = get_path(
            invoice.period,
            invoice.document_id,
            parsed.xml_name,
        )

        store_file(parsed.xml_bytes, destionation, parsed.xml_name)

        return self.create(
            CreditNoteCreate(
                document_id=cn.document_id,
                invoice_id=invoice.id,
                issue_date=cn.issue_date,
                xml_file_path=file_path,
                discrepancy_response_code=cn.discrepancy_response_code,
                discrepancy_description=cn.discrepancy_description,
            ),
        )

    def update(self, id: str, data: CreditNoteUpdate) -> CreditNote:
        cn = self.get_by_id(id)
        return self.repository.update(cn, data.model_dump(exclude_unset=True))

    def delete(self, id: str) -> None:
        cn = self.get_by_id(id)
        for path_attr in ["pdf_file_path", "zip_file_path", "xml_file_path"]:
            val = getattr(cn, path_attr)
            if val:
                file_path = STORAGE_PATH / val
                if file_path.exists() and file_path.is_file():
                    os.remove(file_path)
        self.repository.delete(cn)
