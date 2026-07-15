import io
from pathlib import Path
from datetime import datetime, UTC, date
from typing import BinaryIO
import magic
import zipfile
import xml.etree.ElementTree as ET
from typing import TypedDict

# import shutil
from app.config import STORAGE_PATH
from app.core.types import CurrencyType, DocumentType

# SUNAT_TYPES = {
#     DocumentType.INVOICE_ZIP,
#     DocumentType.INVOICE_XML,
#     DocumentType.INVOICE_PDF,
#     DocumentType.DELIVERY_GUIDE_XML,
#     DocumentType.CREDIT_NOTE_XML,
#     DocumentType.CREDIT_NOTE_PDF,
#     DocumentType.CREDIT_NOTE_ZIP,
#     DocumentType.DELIVERY_GUIDE_PDF,
# }

RUC = "20610555536"
SERIE = "E001"  # por el momento la serie siempre es esta

NS = {
    "main": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
}


def get_text(root: ET.Element, tag: str) -> str | None:
    node = root.find(tag, NS)
    return node.text.strip() if node is not None and node.text else None


def find_all(root: ET.Element, xpath: str) -> list[str]:
    return [n.text.strip() for n in root.findall(xpath, NS) if n is not None and n.text]


def is_prepayment_invoice(root: ET.Element) -> bool:
    invoice_type = root.find("cbc:InvoiceTypeCode", NS)
    return invoice_type is not None and invoice_type.get("listID") in {"0104", "0204"}


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


class InvoiceFromZip(TypedDict):
    period: str
    serie: str
    invoice_id: str
    sequential_number: int
    issue_date: date
    customer_name: str
    customer_ruc: str
    currency: CurrencyType
    total_amount: float


def require(value: str | None, field: str) -> str:
    if value is None:
        raise ValueError(f"El campo {field} es obligatorio")
    return value


def parse_invoice_xml(xml_content: bytes) -> InvoiceFromZip:

    root = ET.fromstring(xml_content)

    mapping = {
        "full_id": "cbc:ID",
        "issue_date": "cbc:IssueDate",
        "customer_ruc": "cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID",
        "customer_name": "cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName",
        "currency": "cbc:DocumentCurrencyCode",
        "total_amount": "cac:LegalMonetaryTotal/cbc:PayableAmount",
    }
    raw = {key: get_text(root, path) for key, path in mapping.items()}

    missing = [k for k, v in raw.items() if v is None]
    if missing:
        raise ValueError(f"Campos obligatorios ausentes en XML: {missing}")

    invoice_id = require(raw["full_id"], "full_id")
    serie, number = invoice_id.split("-")
    issue_date = require(raw["issue_date"], "issue_date")
    period = issue_date.replace("-", "")[:6]

    return InvoiceFromZip(
        period=period,
        serie=serie,
        invoice_id=invoice_id,
        sequential_number=int(number),
        issue_date=datetime.fromisoformat(issue_date),
        customer_name=require(raw["customer_name"], "customer_name"),
        customer_ruc=require(raw["customer_ruc"], "customer_ruc"),
        currency=CurrencyType(raw["currency"]),
        total_amount=float(require(raw["total_amount"], "total_amount")),
    )


def parse_zip_invoice(content: bytes) -> InvoiceFromZip | None:
    buffer = io.BytesIO(content)

    if not zipfile.ZipFile(buffer):
        return None

    buffer.seek(0)  # defensivo
    with zipfile.ZipFile(buffer, "r") as z:
        xml_name = next((f for f in z.namelist() if f.lower().endswith(".xml")), None)
        if not xml_name:
            return None
        return parse_invoice_xml(z.read(xml_name))


def _parse_credit_note_xml(xml_content: bytes) -> dict | None:
    root = ET.fromstring(xml_content)

    credit_note_id = get_text(root, "cbc:ID")
    issue_date = get_text(root, "cbc:IssueDate")
    invoice_ref_id = get_text(root, ".//cac:InvoiceDocumentReference/cbc:ID")

    invoice_id = require(invoice_ref_id, "invoice_ref_id")
    issue_date = require(issue_date, "issue_date")

    return {
        "credit_note_id": require(credit_note_id, "credit_note_id"),
        "invoice_id": invoice_id.strip().replace(" ", ""),  # ej. "E001-1820"
        "issue_date": datetime.fromisoformat(issue_date),
    }


def parse_credit_note_zip(content: bytes) -> dict | None:
    buffer = io.BytesIO(content)
    with zipfile.ZipFile(buffer, "r") as z:
        xml_name = next((f for f in z.namelist() if f.lower().endswith(".xml")), None)
        if not xml_name:
            return None
        return _parse_credit_note_xml(z.read(xml_name))


def get_path(period: str, invoice_id: str, filename: str) -> tuple[Path, str]:
    relative_path = Path(period) / "VENTAS" / invoice_id

    destination = STORAGE_PATH / relative_path
    file_path = (relative_path / filename).as_posix()

    return destination, file_path


class DeliveryNoteFromXml(TypedDict):
    document_id: str
    issue_date: date
    agency_name: str | None
    invoice_references: list[str]


def parse_guide_xml_data(xml_content: bytes) -> DeliveryNoteFromXml:
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

    return DeliveryNoteFromXml(
        document_id=document_id,
        issue_date=datetime.fromisoformat(issue_date),
        agency_name=agency_name,
        invoice_references=invoice_references,
    )
