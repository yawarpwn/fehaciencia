import uuid
from sqlmodel import Session
import os
from app.core.errors import (
    NotFoundAppError,
    ResourseAlreadyExistsAppError,
    ValidationAppError,
)
from app.config import STORAGE_PATH
from app.core.serializer import serialize_delivery_note
from app.core.utils.helpers import (
    get_path,
    parse_delivery_note,
    store_file,
    parse_despatch_advice,
)
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

    def get_by_id(self, id: str) -> DeliveryNote | None:
        return self.repository.get_by_id(id)

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

        if delivery_note is None:
            raise NotFoundAppError(f"Guía de remisión {id} no encontrada")

        if delivery_note.pdf_file_path is not None:
            raise ResourseAlreadyExistsAppError(
                f"Guía de remisión {delivery_note.document_id} ya tiene un pdf"
            )

        last_invoice = delivery_note.sales_invoices[-1]

        if not last_invoice:
            raise NotFoundAppError(
                f"Factura relacion a  {delivery_note.document_id} no encontrada"
            )

        destination, relative_path = get_path(
            last_invoice.period, last_invoice.document_id, filename
        )
        store_file(content, destination, filename)

        return self.repository.update(
            delivery_note, data_dict={"pdf_file_path": relative_path}
        )

    def create_from_xml(self, content: bytes, filename: str | None) -> DeliveryNote:
        if filename is None:
            raise ValidationAppError("No se pudo obtener el nombre del archivo")

        dn = parse_delivery_note(content)

        if self.repository.get_by_document_id(dn.document_id):
            raise ResourseAlreadyExistsAppError(
                f"Guía de remisión {dn.document_id} ya existe"
            )

        delivery_note_id = str(uuid.uuid4())
        xml_file_path = None
        invoices = []

        for invoice_document_id in dn.invoice_references:
            invoice = self.sale_invoice_repo.get_by_document_id(invoice_document_id)

            if invoice is None:
                raise NotFoundAppError(f"Factura {invoice_document_id} no encontrada")

            invoices.append(invoice)

        if len(invoices) == 0:
            raise ValidationAppError(
                "No se encontraron facturas relacionadas a la guía de remisión"
            )

        destination, file_path = get_path(
            invoices[0].period,
            invoices[0].document_id,
            filename,
        )

        store_file(content, destination, filename)
        xml_file_path = file_path

        delivery_note = self.repository.create(
            DeliveryNote(
                id=delivery_note_id,
                document_id=dn.document_id,
                issue_date=dn.issue_date,
                is_agency_shipment=bool(dn.agency_name),
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
        if dn is None:
            raise NotFoundAppError(f"Guía de remisión {delivery_note_id} no encontrada")
        return self.repository.update(dn, data.model_dump(exclude_unset=True))

    def delete(self, delivery_note_id: str) -> None:
        dn = self.get_by_id(delivery_note_id)

        if dn is None:
            raise NotFoundAppError(f"Guía de remisión {delivery_note_id} no encontrada")

        for path_attr in ["pdf_file_path", "zip_file_path", "xml_file_path"]:
            val = getattr(dn, path_attr)
            if val:
                file_path = STORAGE_PATH / val
                if file_path.exists() and file_path.is_file():
                    os.remove(file_path)
        self.repository.delete(dn)
