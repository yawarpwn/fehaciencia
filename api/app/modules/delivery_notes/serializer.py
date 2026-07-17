from app.core.utils import get_file_url
from app.modules.delivery_notes.schema import DeliveryNoteOut
from app.modules.delivery_notes.model import DeliveryNote


def serialize_delivery_note(doc: DeliveryNote) -> DeliveryNoteOut:
    return DeliveryNoteOut(
        id=doc.id,
        document_id=doc.document_id,
        issue_date=doc.issue_date,
        pdf_file_url=get_file_url(doc.pdf_file_path) if doc.pdf_file_path else None,
        xml_file_url=get_file_url(doc.xml_file_path),
        is_agency_shipment=doc.is_agency_shipment,
        sales_invoices=doc.sales_invoices,
    )
