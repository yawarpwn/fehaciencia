# app/sales_invoices/document_rules.py
from dataclasses import dataclass
from enum import Enum

AMOUNT_THRESHOLD = 2000  # Monto a partir del cual los documentos son obligatorios


class InvoiceStatus(str, Enum):  # noqa: F821
    COMPLETE = "COMPLETE"
    VOIDED = "VOIDED"
    INCOMPLETE = "INCOMPLETE"
    ADVANCE = "ADVANCE"


@dataclass
class MissingResult:
    status: InvoiceStatus
    missing: list[str]


def compute_missing(
    present_types: set[str],
    total_amount: float,
    is_agency_shipment: bool,
    has_credit_note: bool,
    is_advance: bool,
) -> MissingResult:
    if has_credit_note:
        return MissingResult(status=InvoiceStatus.VOIDED, missing=[])

    if is_advance:
        return MissingResult(status=InvoiceStatus.ADVANCE, missing=[])

    missing: list[str] = []
    requires_fehaciencia = total_amount >= AMOUNT_THRESHOLD

    if requires_fehaciencia:
        if "DELIVERY_GUIDE" not in present_types:
            missing.append("Guía de remisión")

        # Si es envío por agencia, la guía firmada NO es obligatoria
        if not is_agency_shipment and "DELIVERY_GUIDE_SIGNED" not in present_types:
            missing.append("Guía de remisión firmada")

        if "PHOTO" not in present_types:
            missing.append("Fotos de entrega")

        if "PAYMENT_VOUCHER" not in present_types:
            missing.append("Voucher de depósito")

    if is_agency_shipment and "AGENCY_GUIDE" not in present_types:
        missing.append("Guía de agencia")

    status = InvoiceStatus.COMPLETE if len(missing) == 0 else InvoiceStatus.INCOMPLETE

    return MissingResult(status=status, missing=missing)
