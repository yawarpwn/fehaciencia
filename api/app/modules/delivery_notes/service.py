import uuid
from sqlmodel import Session
import os
from app.core.errors import (
    NotFoundAppError,
    ResourseAlreadyExistsAppError,
    ValidationAppError,
)
from app.config import STORAGE_PATH
from app.core.serializer import serialize_credit_note, serialize_delivery_note
from app.core.utils.helpers import get_path, parse_guide_xml_data, store_file
from app.modules.credit_notes import repository
from app.modules.sales_invoices import document_rules
from app.modules.sales_invoices.repository import SaleInvoiceRepository
from .model import DeliveryNote, DeliveryNoteReference
from .schema import DeliveryNoteCreate, DeliveryNoteOut, DeliveryNoteUpdate
from .repository import DeliveryNoteRepository, DeliveryNoteReferenceRepository


class DeliveryNoteService:
    def __init__(self, session: Session):
        self.repository = DeliveryNoteRepository(session)
        self.sale_invoice_repo = SaleInvoiceRepository(session)
        self.reference_repo = DeliveryNoteReferenceRepository(session)

    def get_all(self) -> list[DeliveryNote]:
        return self.repository.get_all()

    def get_by_id(self, id: str) -> DeliveryNoteOut:
        dn = self.repository.get_by_id(id)
        if not dn:
            raise NotFoundAppError(f"Guía de remisión con id {id} no encontrada")
        return serialize_delivery_note(dn)

    def get_by_document_id(self, delivery_note_id: str) -> DeliveryNote:
        dn = self.repository.get_by_document_id(delivery_note_id)
        if not dn:
            raise NotFoundAppError(
                f"Guía de remisión con id {delivery_note_id} no encontrada"
            )
        return dn

    def create(self, data: DeliveryNoteCreate) -> DeliveryNote:
        dn = DeliveryNote(**data.model_dump())
        return self.repository.create(dn)

    def insert_pdf(self, id: str, content: bytes, filename: str | None):

        if filename is None:
            raise ValidationAppError("No se pudo obtener el nombre del archivo")

        delivery_note = self.get_by_id(id)
        print("delivery_note", delivery_note)
        # invoice = self.sales_invoices_repo.get_by_id(delivery_note.invoice_id)

        # if delivery_note is None:
        #     raise NotFoundAppError(f"Nota de crédito {id} no encontrada")
        #
        # if invoice is None:
        #     raise NotFoundAppError(f"Factura {id} no encontrada")
        #
        # destination, relative_path = get_path(
        #     invoice.period, invoice.invoice_id, filename
        # )
        # store_file(content, destination, filename)
        #
        # self.repository.update(delivery_note, data_dict={"pdf_file_path": relative_path})
        return {"mee": "mee"}

    def create_from_xml(self, content: bytes, filename: str | None) -> DeliveryNote:
        if filename is None:
            raise ValidationAppError("No se pudo obtener el nombre del archivo")

        data = parse_guide_xml_data(content)

        guide_document_id = data["document_id"]

        if self.repository.get_by_document_id(guide_document_id):
            print("aca nunca entra")
            raise ResourseAlreadyExistsAppError(
                f"Guía de remisión {guide_document_id} ya existe"
            )

        delivery_note_id = str(uuid.uuid4())
        xml_file_path = None

        invoices = []

        for invoice_document_id in data["invoice_references"]:
            invoice = self.sale_invoice_repo.get_by_invoice_id(invoice_document_id)

            if invoice is None:
                raise NotFoundAppError(f"Factura {invoice_document_id} no encontrada")

            invoices.append(invoice)

        if invoices:
            destination, relative_path = get_path(
                invoices[0].period,
                invoices[0].invoice_id,
                filename,
            )

            store_file(content, destination, filename)
            xml_file_path = relative_path

        delivery_note = self.repository.create(
            DeliveryNote(
                id=delivery_note_id,
                document_id=guide_document_id,
                issue_date=data["issue_date"],
                is_agency_shipment=bool(data["agency_name"]),
                xml_file_path=xml_file_path,
            )
        )

        for invoice in invoices:
            self.reference_repo.create(
                DeliveryNoteReference(
                    delivery_note_id=delivery_note_id,
                    invoice_id=invoice.id,
                )
            )

        return delivery_note

    def update(self, delivery_note_id: str, data: DeliveryNoteUpdate) -> DeliveryNote:
        dn = self.get_by_id(delivery_note_id)
        return self.repository.update(dn, data.model_dump(exclude_unset=True))

    def delete(self, delivery_note_id: str) -> None:
        dn = self.get_by_id(delivery_note_id)
        for path_attr in ["pdf_file_path", "zip_file_path", "xml_file_path"]:
            val = getattr(dn, path_attr)
            if val:
                file_path = STORAGE_PATH / val
                if file_path.exists() and file_path.is_file():
                    os.remove(file_path)
        self.repository.delete(dn)
