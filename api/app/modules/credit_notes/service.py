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

    def get_by_id(self, credit_note_id: str) -> CreditNote:
        cn = self.repository.get_by_id(credit_note_id)
        if not cn:
            raise NotFoundAppError(
                f"Nota de crédito con id {credit_note_id} no encontrada"
            )
        return cn

    def get_by_credit_note_id(self, credit_note_id: str) -> CreditNote:
        cn = self.repository.get_by_credit_note_id(credit_note_id)
        print("cn", cn)
        if cn is None:
            raise NotFoundAppError(f"Nota de crédito {credit_note_id} no encontrada")
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
            invoice.period, invoice.invoice_id, filename
        )
        store_file(content, destination, filename)

        self.repository.update(credit_note, data_dict={"pdf_file_path": relative_path})

    def create_from_zip(self, content: bytes, filename: str | None):
        if filename is None:
            raise ValidationAppError("No se pudo obtener el nombre del archivo")

        credit_note_from_zip = parse_credit_note_zip(content)

        if credit_note_from_zip is None:
            raise ValidationAppError(f"Error procesando zip {filename}")

        # Buscar sale_invoce por id
        invoice_from_db = self.sales_invoices_repo.get_by_invoice_id(
            credit_note_from_zip["invoice_id"]
        )

        if invoice_from_db is None:
            raise NotFoundAppError(
                f"Factura {credit_note_from_zip['invoice_id']} no encontrada"
            )

        exists = self.repository.get_by_credit_note_id(
            credit_note_from_zip["credit_note_id"]
        )

        if exists is not None:
            raise ResourseAlreadyExistsAppError(
                f"Nota de credito {credit_note_from_zip['credit_note_id']} ya existe"
            )

        destionation, relative_path = get_path(
            invoice_from_db.period, invoice_from_db.invoice_id, filename
        )

        store_file(content, destionation, filename)

        return self.create(
            CreditNoteCreate(
                credit_note_id=credit_note_from_zip["credit_note_id"],
                invoice_id=invoice_from_db.id,
                zip_file_path=relative_path,
                issue_date=credit_note_from_zip["issue_date"],
            ),
        )

    def update(self, credit_note_id: str, data: CreditNoteUpdate) -> CreditNote:
        cn = self.get_by_id(credit_note_id)
        return self.repository.update(cn, data.model_dump(exclude_unset=True))

    def delete(self, credit_note_id: str) -> None:
        cn = self.get_by_id(credit_note_id)
        for path_attr in ["pdf_file_path", "zip_file_path", "xml_file_path"]:
            val = getattr(cn, path_attr)
            if val:
                file_path = STORAGE_PATH / val
                if file_path.exists() and file_path.is_file():
                    os.remove(file_path)
        self.repository.delete(cn)
