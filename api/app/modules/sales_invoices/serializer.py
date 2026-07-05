# app/sales_invoices/serializer.py
from .model import SalesInvoice, SupportingDocument, DocumentType
from .schema import DocumentOut, SalesInvoiceOut
from .document_rules import compute_missing
from app.config import BASE_URL

CREDIT_NOTE_TYPES = {"CREDIT_NOTE_PDF", "CREDIT_NOTE_ZIP", "CREDIT_NOTE_XML"}


def _doc_out(doc: SupportingDocument) -> DocumentOut:
    file_url = f"{BASE_URL}/documents/{doc.file_path}"
    thumbnail_url = file_url if doc.document_type == DocumentType.PHOTO else None
    return DocumentOut(
        id=doc.id,
        documentType=doc.document_type.value,
        fileName=doc.file_name,
        uploadedAt=doc.created_at.strftime("%Y-%m-%d %H:%M"),
        fileUrl=file_url,
        thumbnailUrl=thumbnail_url,
    )


def serialize_invoice(inv: SalesInvoice) -> SalesInvoiceOut:
    by_type: dict[str, list[DocumentOut]] = {}
    for doc in inv.documents:
        by_type.setdefault(doc.document_type.value, []).append(_doc_out(doc))

    present_types = set(by_type.keys())
    has_credit_note = bool(present_types & CREDIT_NOTE_TYPES)

    result = compute_missing(
        present_types=present_types,
        total_amount=inv.total_amount,
        is_agency_shipment=inv.is_agency_shipment,
        has_credit_note=has_credit_note,
    )

    short_name = (
        inv.customer_name[:25] + "..."
        if len(inv.customer_name) > 25
        else inv.customer_name
    )

    credit_notes = by_type.get("CREDIT_NOTE_PDF", [])

    return SalesInvoiceOut(
        id=inv.id,
        invoiceCode=f"{inv.serie}-{inv.number:04d}",
        period=inv.period,
        status=inv.status.value,
        customerRuc=inv.customer_ruc,
        customerName=inv.customer_name,
        customerShortName=short_name,
        totalAmount=inv.total_amount,
        isAdvance=inv.is_advance,
        purchaseOrder=by_type.get("PURCHASE_ORDER", [None])[0],
        deliveryGuides=by_type.get("DELIVERY_GUIDE", []),
        agencyGuides=by_type.get("AGENCY_GUIDE", []),
        signedDeliveryGuides=by_type.get("DELIVERY_GUIDE_SIGNED", []),
        photos=by_type.get("PHOTO", []),
        vouchers=by_type.get("PAYMENT_VOUCHER", []),
        creditNote=credit_notes[0] if credit_notes else None,
        isComplete=result.is_complete,
        missing=result.missing,
        isAgencyShipment=inv.is_agency_shipment,
    )
