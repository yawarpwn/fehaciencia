# app/sales_invoices/document_rules.py
from dataclasses import dataclass

AMOUNT_THRESHOLD = 1000  # Monto a partir del cual los documentos son obligatorios


@dataclass
class MissingResult:
    is_complete: bool
    missing: list[str]


def compute_missing(
    present_types: set[str],
    total_amount: float,
    is_agency_shipment: bool,
    has_credit_note: bool,
) -> MissingResult:
    """
    Calcula qué documentos faltan según las reglas de negocio.

    Reglas:
    - Si tiene nota de crédito → siempre completo, sin requisitos.
    - Si monto >= 1000 → voucher, fotos, guía de remisión y guía firmada son obligatorios.
    - Si la guía indica envío por agencia → guía de agencia obligatoria (sin importar monto).
    - Si monto < 1000 → todos los documentos de fehaciencia son opcionales.
    - Orden de compra: siempre obligatorio (independiente del monto).
    """

    # Nota de crédito: ignora todos los requisitos
    if has_credit_note:
        return MissingResult(is_complete=True, missing=[])

    missing: list[str] = []
    requires_fehaciencia = total_amount >= AMOUNT_THRESHOLD

    # Orden de compra — siempre requerida
    if "PURCHASE_ORDER" not in present_types:
        missing.append("Orden de compra")

    if requires_fehaciencia:
        if "DELIVERY_GUIDE" not in present_types:
            missing.append("Guía de remisión")

        if "DELIVERY_GUIDE_SIGNED" not in present_types:
            missing.append("Guía de remisión firmada")

        if "PHOTO" not in present_types:
            missing.append("Fotos de entrega")

        if "PAYMENT_VOUCHER" not in present_types:
            missing.append("Voucher de depósito")

    # Guía de agencia — requerida si el envío es por agencia, sin importar el monto
    if is_agency_shipment and "AGENCY_GUIDE" not in present_types:
        missing.append("Guía de agencia")

    return MissingResult(is_complete=len(missing) == 0, missing=missing)
