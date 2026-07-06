# app/sales_invoices/serializer.py
from .model import SalesInvoice, SupportingDocument, DocumentType
from .schema import DocumentOut, SalesInvoiceOut
from .document_rules import compute_missing
from app.config import BASE_URL

CREDIT_NOTE_TYPES = {"CREDIT_NOTE_PDF", "CREDIT_NOTE_ZIP", "CREDIT_NOTE_XML"}


def serialize_document(doc: SupportingDocument) -> DocumentOut:
    file_url = f"{BASE_URL}/documents/{doc.file_path}"

    thumbnail_url = None
    if doc.thumbnail_path is not None:
        thumbnail_url = f"{BASE_URL}/documents/{doc.thumbnail_path}"

    return DocumentOut(
        id=doc.id,
        documentType=doc.document_type.value,
        fileName=doc.file_name,
        uploadedAt=doc.created_at.strftime("%Y-%m-%d %H:%M"),
        fileUrl=file_url,
        thumbnailUrl=thumbnail_url,
    )


def serialize_invoice(invoice: SalesInvoice) -> SalesInvoiceOut:
    by_type: dict[str, list[DocumentOut]] = {}
    for doc in invoice.documents:
        by_type.setdefault(doc.document_type.value, []).append(serialize_document(doc))

    present_types = set(by_type.keys())
    has_credit_note = bool(present_types & CREDIT_NOTE_TYPES)

    result = compute_missing(
        present_types=present_types,
        total_amount=invoice.total_amount,
        is_agency_shipment=invoice.is_agency_shipment,
        has_credit_note=has_credit_note,
        is_advance=invoice.is_advance,
    )

    short_name = (
        invoice.customer_name[:25] + "..."
        if len(invoice.customer_name) > 25
        else invoice.customer_name
    )

    credit_notes = by_type.get("CREDIT_NOTE_PDF", [])
    pdf_invoices = by_type.get("INVOICE_PDF", [])

    return SalesInvoiceOut(
        id=invoice.id,
        invoiceId=invoice.invoice_id,
        period=invoice.period,
        status=result.status,
        customerRuc=invoice.customer_ruc,
        customerName=invoice.customer_name,
        customerShortName=short_name,
        totalAmount=invoice.total_amount,
        isAdvance=invoice.is_advance,
        purchaseOrder=by_type.get("PURCHASE_ORDER", [None])[0],
        deliveryGuides=by_type.get("DELIVERY_GUIDE", []),
        agencyGuides=by_type.get("AGENCY_GUIDE", []),
        signedDeliveryGuides=by_type.get("DELIVERY_GUIDE_SIGNED", []),
        photos=by_type.get("PHOTO", []),
        vouchers=by_type.get("PAYMENT_VOUCHER", []),
        creditNote=credit_notes[0] if credit_notes else None,
        pdfFile=pdf_invoices[0] if pdf_invoices else None,
        missing=result.missing,
        isAgencyShipment=invoice.is_agency_shipment,
        issueDate=invoice.issue_date.strftime("%Y-%m-%d"),
    )
