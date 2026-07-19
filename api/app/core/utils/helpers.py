import io
from pathlib import Path
from datetime import datetime, UTC, date
import magic
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass

# import shutil
from app.config import STORAGE_PATH
from app.core.types import CurrencyType, DocumentType

RUC = "20610555536"
SERIE = "E001"  # por el momento la serie siempre es esta

NS = {
    "main": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
}


def get_text(root: ET.Element, path: str) -> str | None:
    node = root.find(path, NS)
    return node.text.strip() if node is not None and node.text else None


def find_all(root: ET.Element, xpath: str) -> list[str]:
    return [n.text.strip() for n in root.findall(xpath, NS) if n is not None and n.text]


# def is_prepayment_invoice(root: ET.Element) -> bool:
#     invoice_type = root.find("cbc:InvoiceTypeCode", NS)
#     return invoice_type is not None and invoice_type.get("listID") in {"0104", "0204"}


def generate_unique_filename(original_name: str, doc_type: DocumentType) -> str:
    # if doc_type in SUNAT_TYPES:
    #     return original_name

    ext = Path(original_name).suffix
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"{doc_type.value.lower()}_{timestamp}{ext}"


def detect_mime_type(file: bytes) -> str:
    return magic.from_buffer(file, mime=True)


def store_file(content: bytes, target_dir: Path, target_name: str) -> Path:
    """Copia el archivo al directorio de destino y devuelve la ruta destino."""
    safe_name = Path(target_name).name
    target_dir.mkdir(parents=True, exist_ok=True)
    destination = target_dir / safe_name
    destination.write_bytes(content)
    # shutil.copy2(source, destination)
    return destination


def utc_now() -> datetime:
    return datetime.now(UTC)


def require(value: str | None, field: str) -> str:
    if value is None:
        raise ValueError(f"El campo {field} es obligatorio")
    return value


@dataclass
class InvoiceData:
    period: str
    serie: str
    document_id: str
    sequential_number: int
    issue_date: date
    customer_name: str
    customer_ruc: str
    currency: CurrencyType
    total_amount: float
    is_prepayment_invoice: bool
    prepayment_reference_invoice: str | None
    payment_method: str


@dataclass
class InvoiceFile:
    xml_name: str
    xml_bytes: bytes
    data: InvoiceData


# def is_prepayment_invoice(root) -> bool:
#     tipo = root.find(".//cbc:InvoiceTypeCode", NS)
#     if tipo is not None and tipo.attrib.get("listID", "") in ("0104", "0204"):
#         return True
#     for desc in root.findall(".//cac:Item/cbc:Description", NS):
#         if desc.text and "anticipo" in desc.text.lower():
#             return True
#     return False


# def is_prepayment_invoice(root) -> bool:
#     for desc in root.findall("cac:InvoiceLine/cac:Item/cbc:Description", NS):
#         if desc.text and (
#             "ANTICIPO" in desc.text.upper() or "PAGO ANTICIPADO" in desc.text.upper()
#         ):
#             return True
#     return False
#
#
# def prepayment_reference_invoice(root) -> str | None:
#     doc_ref = root.find("cac:AdditionalDocumentReference", NS)
#     if doc_ref is not None:
#         tipo = get_text(doc_ref, "cbc:DocumentType")
#         if tipo and "ANTICIPO" in tipo.upper():
#             return get_text(doc_ref, "cbc:ID")
#     return None


CODIGOS_TIPO_OPERACION_ANTICIPO = {"0104", "0204"}


def is_prepayment_invoice(root):
    tipo = root.find("cbc:InvoiceTypeCode", NS)
    if tipo is not None:
        list_id = tipo.attrib.get("listID", "")
        if list_id in CODIGOS_TIPO_OPERACION_ANTICIPO:
            return True
    return False


def prepayment_reference_invoice(root):
    doc_ref = root.find("cac:AdditionalDocumentReference", NS)
    if doc_ref is not None:
        tipo = get_text(doc_ref, "cbc:DocumentType")
        if tipo and "ANTICIPO" in tipo.upper():
            return get_text(doc_ref, "cbc:ID")
    return None


def parse_invoice_data(xml_content: bytes) -> InvoiceData:

    root = ET.fromstring(xml_content)

    # prepaid = root.find("cac:PrepaidPayment", NS)
    # if prepaid is not None:
    #     datos["pago_anticipado"] = _text(prepaid, "cbc:PaidAmount")

    mapping = {
        "full_id": "cbc:ID",
        "issue_date": "cbc:IssueDate",
        "customer_ruc": "cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID",
        "customer_name": "cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName",
        "currency": "cbc:DocumentCurrencyCode",
        "total_amount": "cac:LegalMonetaryTotal/cbc:PayableAmount",
        "payment_method": "cac:PaymentTerms/cbc:PaymentMeansID",
        "is_prepaid": "cbc:PaidAmount",
    }

    raw = {key: get_text(root, path) for key, path in mapping.items()}
    document_id = require(raw["full_id"], "full_id")
    serie, number = document_id.split("-")
    issue_date = require(raw["issue_date"], "issue_date")
    period = issue_date.replace("-", "")[:6]

    return InvoiceData(
        period=period,
        serie=serie,
        document_id=document_id,
        sequential_number=int(number),
        issue_date=datetime.fromisoformat(issue_date),
        customer_name=require(raw["customer_name"], "customer_name"),
        customer_ruc=require(raw["customer_ruc"], "customer_ruc"),
        currency=CurrencyType(raw["currency"]),
        total_amount=float(require(raw["total_amount"], "total_amount")),
        is_prepayment_invoice=is_prepayment_invoice(root),
        prepayment_reference_invoice=prepayment_reference_invoice(root),
        payment_method=require(raw["payment_method"], "payment_method"),
    )


def parse_zip_invoice(content: bytes) -> InvoiceFile | None:
    buffer = io.BytesIO(content)

    try:
        with zipfile.ZipFile(buffer, "r") as z:
            xml_name = next(
                (f for f in z.namelist() if f.lower().endswith(".xml")), None
            )
            if not xml_name:
                return None

            xml_bytes = z.read(xml_name)
            data = parse_invoice_data(z.read(xml_name))

            return InvoiceFile(xml_bytes=xml_bytes, xml_name=xml_name, data=data)
    except zipfile.BadZipFile:
        return None


@dataclass
class CreditNoteData:
    document_id: str
    issue_date: date
    discrepancy_reference_id: str
    discrepancy_response_code: str
    discrepancy_description: str


@dataclass
class CreditNoteFile:
    xml_bytes: bytes
    xml_name: str
    data: CreditNoteData


def parse_credit_note(xml_content: bytes) -> CreditNoteData:
    root = ET.fromstring(xml_content)

    credit_note_id = get_text(root, "cbc:ID")
    issue_date = get_text(root, "cbc:IssueDate")
    invoice_ref_id = get_text(root, ".//cac:InvoiceDocumentReference/cbc:ID")

    invoice_document_id = require(invoice_ref_id, "invoice_ref_id")
    issue_date = require(issue_date, "issue_date")

    discrepancy_ref_id = get_text(root, ".//cac:DiscrepancyResponse/cbc:ReferenceID")
    discrepancy_ref_id = require(discrepancy_ref_id, "discrepancy_ref_id")
    discrepancy_response_code = get_text(
        root, ".//cac:DiscrepancyResponse/cbc:ResponseCode"
    )
    discrepancy_description = get_text(
        root, ".//cac:DiscrepancyResponse/cbc:Description"
    )

    return CreditNoteData(
        document_id=require(credit_note_id, "credit_note_id"),
        # "invoice_document_id": invoice_document_id.strip().replace(" ", ""),
        issue_date=datetime.fromisoformat(issue_date),
        discrepancy_reference_id=discrepancy_ref_id.strip().replace(" ", ""),
        discrepancy_response_code=require(
            discrepancy_response_code, "discrepancy_response_code"
        ),
        discrepancy_description=require(
            discrepancy_description, "discrepancy_description"
        ),
    )


def parse_credit_note_zip(content: bytes) -> CreditNoteFile | None:

    buffer = io.BytesIO(content)
    with zipfile.ZipFile(buffer, "r") as z:
        xml_name = next((f for f in z.namelist() if f.lower().endswith(".xml")), None)
        if not xml_name:
            return None

        xml_bytes = z.read(xml_name)
        parsed_data = parse_credit_note(xml_bytes)

        return CreditNoteFile(xml_bytes=xml_bytes, xml_name=xml_name, data=parsed_data)


def get_path(period: str, document_id: str, filename: str) -> tuple[Path, str]:
    relative_path = Path(period) / "VENTAS" / document_id

    destination = STORAGE_PATH / relative_path
    file_path = (relative_path / filename).as_posix()

    return destination, file_path


def get_file_url(file_path: str) -> str:
    return f"/documents/{file_path}"


def parse_despatch_advice(xml_content: bytes) -> dict:
    root = ET.fromstring(xml_content)

    # --- Identificación del documento ---
    document_id = get_text(root, "cbc:ID")
    issue_date = get_text(root, "cbc:IssueDate")
    issue_time = get_text(root, "cbc:IssueTime")
    despatch_type_code = get_text(
        root, "cbc:DespatchAdviceTypeCode"
    )  # Catálogo 01 (09 = Guía Remitente)
    note = get_text(root, "cbc:Note")

    # --- Documento relacionado (ej. Factura) ---
    related_doc_id = get_text(root, ".//cac:AdditionalDocumentReference/cbc:ID")
    related_doc_type_code = get_text(
        root, ".//cac:AdditionalDocumentReference/cbc:DocumentTypeCode"
    )
    related_doc_type = get_text(
        root, ".//cac:AdditionalDocumentReference/cbc:DocumentType"
    )
    related_doc_issuer_ruc = get_text(
        root, ".//cac:AdditionalDocumentReference//cac:IssuerParty//cbc:ID"
    )

    # --- Remitente (emisor) ---
    supplier_ruc = get_text(root, ".//cac:DespatchSupplierParty//cbc:ID")
    supplier_name = get_text(root, ".//cac:DespatchSupplierParty//cbc:RegistrationName")

    # --- Destinatario ---
    customer_id = get_text(root, ".//cac:DeliveryCustomerParty//cbc:ID")
    customer_name = get_text(root, ".//cac:DeliveryCustomerParty//cbc:RegistrationName")

    # --- Datos del traslado (Shipment) ---
    shipment_id = get_text(root, ".//cac:Shipment/cbc:ID")
    handling_code = get_text(
        root, ".//cac:Shipment/cbc:HandlingCode"
    )  # Catálogo 20 (motivo traslado)
    handling_instructions = get_text(root, ".//cac:Shipment/cbc:HandlingInstructions")
    gross_weight = get_text(root, ".//cac:Shipment/cbc:GrossWeightMeasure")
    gross_weight_unit = None
    gw_el = root.find(".//cac:Shipment/cbc:GrossWeightMeasure", NS)
    if gw_el is not None:
        gross_weight_unit = gw_el.get("unitCode")

    # --- Modalidad de traslado y transportista ---
    transport_mode_code = get_text(
        root, ".//cac:ShipmentStage/cbc:TransportModeCode"
    )  # Catálogo 18
    carrier_ruc = get_text(root, ".//cac:CarrierParty//cbc:ID")
    carrier_name = get_text(root, ".//cac:CarrierParty//cbc:RegistrationName")
    carrier_mtc_registration = get_text(root, ".//cac:CarrierParty//cbc:CompanyID")
    loading_date = get_text(root, ".//cac:LoadingTransportEvent/cbc:OccurrenceDate")

    # --- Direcciones (partida / llegada) ---
    delivery_ubigeo = get_text(root, ".//cac:DeliveryAddress/cbc:ID")
    delivery_address = get_text(
        root, ".//cac:DeliveryAddress//cac:AddressLine/cbc:Line"
    )

    despatch_ubigeo = get_text(root, ".//cac:DespatchAddress/cbc:ID")
    despatch_address = get_text(
        root, ".//cac:DespatchAddress//cac:AddressLine/cbc:Line"
    )

    # --- Detalle de ítems trasladados ---
    lines = []
    for line in root.findall("cac:DespatchLine", NS):
        qty_el = line.find("cbc:DeliveredQuantity", NS)
        lines.append(
            {
                "line_id": get_text(line, "cbc:ID"),
                "delivered_quantity": qty_el.text if qty_el is not None else None,
                "unit_code": qty_el.get("unitCode") if qty_el is not None else None,
                "order_line_ref": get_text(
                    line, ".//cac:OrderLineReference/cbc:LineID"
                ),
                "item_description": get_text(line, ".//cac:Item/cbc:Description"),
                "item_seller_id": get_text(
                    line, ".//cac:Item//cac:SellersItemIdentification/cbc:ID"
                ),
            }
        )

    return {
        # Documento
        "document_id": require(document_id, "document_id"),
        "issue_date": datetime.fromisoformat(require(issue_date, "issue_date")),
        "issue_time": issue_time,
        "despatch_type_code": despatch_type_code,
        "note": note,
        # Documento relacionado
        "related_document_id": related_doc_id,
        "related_document_type_code": related_doc_type_code,
        "related_document_type": related_doc_type,
        "related_document_issuer_ruc": related_doc_issuer_ruc,
        # Remitente / Destinatario
        "supplier_ruc": supplier_ruc,
        "supplier_name": supplier_name,
        "customer_id": customer_id,
        "customer_name": customer_name,
        # Traslado
        "shipment_id": shipment_id,
        "handling_code": handling_code,
        "handling_instructions": handling_instructions,
        "gross_weight": gross_weight,
        "gross_weight_unit": gross_weight_unit,
        "transport_mode_code": transport_mode_code,
        "loading_date": loading_date,
        # Transportista
        "carrier_ruc": carrier_ruc,
        "carrier_name": carrier_name,
        "carrier_mtc_registration": carrier_mtc_registration,
        # Direcciones
        "despatch_ubigeo": despatch_ubigeo,
        "despatch_address": despatch_address,
        "delivery_ubigeo": delivery_ubigeo,
        "delivery_address": delivery_address,
        # Detalle
        "lines": lines,
    }


@dataclass
class DeliveryData:
    document_id: str
    issue_date: date
    agency_name: str | None
    invoice_references: list[str]


def parse_delivery_note(xml_content: bytes) -> DeliveryData:
    root = ET.fromstring(xml_content)

    mapping = {
        "delivery_note_id": "cbc:ID",
        "issue_date": "cbc:IssueDate",
        "agency_name": ".//cac:CarrierParty//cac:PartyLegalEntity//cbc:RegistrationName",
    }
    # agency_name = get_text(
    #     root, ".//cac:CarrierParty//cac:PartyLegalEntity//cbc:RegistrationName"
    # )

    raw = {key: get_text(root, path) for key, path in mapping.items()}

    # missing = [k for k, v in raw.items() if v is None]
    # if missing:
    #     raise ValueError(f"Campos obligatorios ausentes en XML: {missing}")

    document_id = require(raw["delivery_note_id"], "delivery_note_id")
    issue_date = require(raw["issue_date"], "issue_date")
    agency_name = raw["agency_name"]
    invoice_references = find_all(root, ".//cac:AdditionalDocumentReference/cbc:ID")

    return DeliveryData(
        document_id=document_id,
        issue_date=datetime.fromisoformat(issue_date),
        agency_name=agency_name,
        invoice_references=invoice_references,
    )
