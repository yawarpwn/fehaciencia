import io
from pathlib import Path
from datetime import datetime, UTC, date
from typing import BinaryIO
import magic
import zipfile
import xml.etree.ElementTree as ET
from typing import TypedDict
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


@dataclass
class InvoiceFile:
    xml_name: str
    xml_bytes: bytes
    data: InvoiceData


def parse_invoice_data(xml_content: bytes) -> InvoiceData:

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
