from dataclasses import dataclass
from enum import Enum

AMOUNT_THRESHOLD = 1000  # Monto a partir del cual los documentos son obligatorios


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
    has_delivery_note: bool,
) -> MissingResult:

    if has_credit_note:
        return MissingResult(status=InvoiceStatus.VOIDED, missing=[])

    if is_advance:
        return MissingResult(status=InvoiceStatus.ADVANCE, missing=[])

    missing: list[str] = []
    requires_fehaciencia = total_amount >= AMOUNT_THRESHOLD

    if requires_fehaciencia:
        if not has_delivery_note:
            missing.append("Guía Remisión")

        # Si es envío por agencia, la guía firmada NO es obligatoria
        if not is_agency_shipment and "DELIVERY_GUIDE_SIGNED" not in present_types:
            missing.append("Guía firmada")

        if "PHOTO" not in present_types:
            missing.append("Fotos")

        if "PAYMENT_VOUCHER" not in present_types:
            missing.append("Depósito")

    if is_agency_shipment and "AGENCY_GUIDE" not in present_types:
        missing.append("Guía Agencia")

    status = InvoiceStatus.COMPLETE if len(missing) == 0 else InvoiceStatus.INCOMPLETE

    return MissingResult(status=status, missing=missing)
