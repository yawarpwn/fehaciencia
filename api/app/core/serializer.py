# app/sales_invoices/serializer.py
from app.modules.credit_notes.model import CreditNote
from app.modules.credit_notes.schema import CreditNoteOut
from app.modules.delivery_notes.model import DeliveryNote
from app.modules.delivery_notes.schema import DeliveryNoteOut
from app.modules.sales_invoices.model import SalesInvoice
from app.modules.sales_invoices.schema import DocumentOut, SalesInvoiceOut

from app.modules.sales_invoices.document_rules import compute_missing
from app.modules.supporting_documents.model import SupportingDocument
from app.core.types import DocumentType
# from app.config import BASE_URL


def get_file_url(file_path: str | None) -> str:
    return f"/documents/{file_path}"


def serialize_document(doc: SupportingDocument) -> DocumentOut:
    thumbnail_url = None
    if doc.thumbnail_path is not None:
        thumbnail_url = get_file_url(doc.thumbnail_path)

    return DocumentOut(
        id=doc.id,
        document_type=doc.document_type.value,
        file_name=doc.file_name,
        file_url=get_file_url(doc.file_path),
        thumbnail_url=thumbnail_url,
    )


def serialize_credit_note(doc: CreditNote) -> CreditNoteOut:
    return CreditNoteOut(
        id=doc.id,
        invoice_id=doc.invoice_id,
        credit_note_id=doc.credit_note_id,
        issue_date=doc.issue_date,
        pdf_file_url=get_file_url(doc.pdf_file_path) if doc.pdf_file_path else None,
        zip_file_url=get_file_url(doc.zip_file_path) if doc.zip_file_path else None,
        xml_file_url=get_file_url(doc.xml_file_path) if doc.xml_file_path else None,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


def serialize_delivery_note(doc: DeliveryNote) -> DeliveryNoteOut:
    return DeliveryNoteOut(
        id=doc.id,
        document_id=doc.document_id,
        issue_date=doc.issue_date,
        pdf_file_url=get_file_url(doc.pdf_file_path) if doc.pdf_file_path else None,
        zip_file_url=get_file_url(doc.zip_file_path) if doc.zip_file_path else None,
        xml_file_url=get_file_url(doc.xml_file_path) if doc.xml_file_path else None,
        is_agency_shipment=doc.is_agency_shipment,
        sales_invoices=doc.sales_invoices,
    )


def serialize_invoice(invoice: SalesInvoice) -> SalesInvoiceOut:
    by_type: dict[str, list[DocumentOut]] = {}
    for doc in invoice.documents:
        by_type.setdefault(doc.document_type.value, []).append(serialize_document(doc))

    present_types = set(by_type.keys())
    has_credit_note = bool(invoice.credit_notes)

    is_agency_shipment = False
    for dn in invoice.delivery_notes:
        if dn.is_agency_shipment and dn.document_id:
            is_agency_shipment = True

    has_credit_note = False
    for cn in invoice.credit_notes:
        if cn:
            has_credit_note = True

    result = compute_missing(
        present_types=present_types,
        total_amount=invoice.total_amount,
        is_agency_shipment=is_agency_shipment,
        has_credit_note=has_credit_note,
        has_delivery_note=len(invoice.delivery_notes) > 0,
        is_advance=invoice.is_advance,
    )

    short_name = (
        invoice.customer_name[:25] + "..."
        if len(invoice.customer_name) > 25
        else invoice.customer_name
    )

    # credit_notes = by_type.get("CREDIT_NOTE_PDF", [])
    # pdf_invoices = by_type.get("INVOICE_PDF", [])

    # purchaseOrder=by_type.get("PURCHASE_ORDER", [None])[0],
    # pdfFile=pdf_invoices[0] if pdf_invoices else None,
    # missing=result.missing,
    # issueDate=invoice.issue_date.strftime("%Y-%m-%d"),
    credit_notes = [serialize_credit_note(nc) for nc in invoice.credit_notes]
    delivery_notes = [serialize_delivery_note(dn) for dn in invoice.delivery_notes]
    # payment_vouchers = [serialize_document(doc) for doc in payment_vouchers]

    return SalesInvoiceOut(
        id=invoice.id,
        invoice_id=invoice.invoice_id,
        period=invoice.period,
        customer_ruc=invoice.customer_ruc,
        customer_name=invoice.customer_name,
        customer_short_name=short_name,
        total_amount=invoice.total_amount,
        is_advance=invoice.is_advance,
        issue_date=invoice.issue_date,
        credit_notes=credit_notes,
        purchase_order=by_type.get(DocumentType.PURCHASE_ORDER, [None])[0],
        delivery_notes=delivery_notes,
        agency_guides=by_type.get(DocumentType.AGENCY_GUIDE, []),
        signed_delivery_guides=by_type.get(DocumentType.DELIVERY_GUIDE_SIGNED, []),
        photos=by_type.get(DocumentType.PHOTO, []),
        payment_vouchers=by_type.get(DocumentType.PAYMENT_VOUCHER, []),
        pdf_file_url=get_file_url(invoice.pdf_file_path),
        zip_file_url=get_file_url(invoice.zip_file_path),
        missing=result.missing,
        status=result.status,
    )
