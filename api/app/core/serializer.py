from app.modules.sales_invoices.model import SalesInvoice
from app.modules.sales_invoices.schema import DocumentOut, SalesInvoiceOut
from app.modules.sales_invoices.document_rules import compute_missing
from app.modules.supporting_documents.model import SupportingDocument
from app.core.types import DocumentType
from app.modules.credit_notes.serializer import serialize_credit_note
from app.modules.delivery_notes.serializer import serialize_delivery_note
from app.core.utils import get_file_url


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

    credit_notes = [serialize_credit_note(nc) for nc in invoice.credit_notes]
    delivery_notes = [serialize_delivery_note(dn) for dn in invoice.delivery_notes]
    # payment_vouchers = [serialize_document(doc) for doc in payment_vouchers]

    return SalesInvoiceOut(
        id=invoice.id,
        document_id=invoice.document_id,
        period=invoice.period,
        currency=invoice.currency,
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
        pdf_file_url=get_file_url(invoice.pdf_file_path)
        if invoice.pdf_file_path
        else None,
        xml_file_url=get_file_url(invoice.xml_file_path),
        missing=result.missing,
        status=result.status,
    )
