from enum import Enum


class CurrencyType(str, Enum):
    PEN = "PEN"
    USD = "USD"


# app/sales_invoices/models.py
class DocumentType(str, Enum):
    # Documentos SUNAT (técnicos, generados automáticamente)
    INVOICE_XML = "INVOICE_XML"
    INVOICE_ZIP = "INVOICE_ZIP"
    INVOICE_PDF = "INVOICE_PDF"
    DELIVERY_GUIDE_XML = "DELIVERY_GUIDE_XML"  # ← de vuelta, es SUNAT técnico
    CREDIT_NOTE_XML = "CREDIT_NOTE_XML"
    CREDIT_NOTE_ZIP = "CREDIT_NOTE_ZIP"
    CREDIT_NOTE_PDF = "CREDIT_NOTE_PDF"

    # Documentos de fehaciencia (sube el usuario)
    PURCHASE_ORDER = "PURCHASE_ORDER"
    DELIVERY_GUIDE_PDF = "DELIVERY_GUIDE"  # PDF guía de remisión SUNAT
    AGENCY_GUIDE = "AGENCY_GUIDE"  # antes CARRIER_RECEIPT
    DELIVERY_GUIDE_SIGNED = "DELIVERY_GUIDE_SIGNED"  # antes SIGNED_SHIPPING_RECEIPT
    PHOTO = "PHOTO"
    PAYMENT_VOUCHER = "PAYMENT_VOUCHER"  # antes BANK_VOUCHER
