# app/sales_invoices/seed.py
import mimetypes
import uuid
import zipfile
import shutil
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, date
from sqlmodel import Session

from app.core.database import engine
from app.modules.sales_invoices.model import (
    SalesInvoice,
    SupportingDocument,
    DocumentType,
)
from app.config import STORAGE_PATH

NAMESPACES = {
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
}

MONTHS = {
    1: "ENERO",
    2: "FEBRERO",
    3: "MARZO",
    4: "ABRIL",
    5: "MAYO",
    6: "JUNIO",
    7: "JULIO",
    8: "AGOSTO",
    9: "SEPTIEMBRE",
    10: "OCTUBRE",
    11: "NOVIEMBRE",
    12: "DICIEMBRE",
}


# ── Helpers ───────────────────────────────────────────────────────────────────


def get_text(root: ET.Element, tag: str) -> str | None:
    node = root.find(tag, NAMESPACES)
    return node.text.strip() if node is not None and node.text else None


def find_all(root: ET.Element, tag: str) -> list[str]:
    node = root.findall(tag, NAMESPACES)
    return [n.text.strip() for n in node]


def find_all_by_pattern(files: list[str], pattern: str) -> list[str]:
    regex = re.compile(pattern, re.IGNORECASE)
    return [f for f in files if regex.match(f)]


def generate_unique_filename(original_name: str, doc_type: DocumentType) -> str:
    ext = Path(original_name).suffix
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"{doc_type.value.lower()}_{timestamp}{ext}"


def detect_mime_type(file_path: Path) -> str:
    mime, _ = mimetypes.guess_type(file_path.name)
    return mime or "application/octet-stream"


def store_file(source: Path, target_dir: Path, target_name: str) -> Path:
    """Copia el archivo al directorio de destino y devuelve la ruta destino."""
    target_dir.mkdir(parents=True, exist_ok=True)
    destination = target_dir / target_name
    shutil.copy2(source, destination)
    return destination


def make_document(
    invoice_id: str,
    doc_type: DocumentType,
    source_path: Path,
    stored_path: Path,
) -> SupportingDocument:
    """Construye un SupportingDocument con todos los campos requeridos."""
    relative_path = stored_path.relative_to(STORAGE_PATH)
    return SupportingDocument(
        id=str(uuid.uuid4()),
        invoice_id=invoice_id,
        document_type=doc_type,
        file_name=stored_path.name,
        file_path=str(relative_path),  # relativo a STORAGE_PATH
        mime_type=detect_mime_type(source_path),
        file_size=source_path.stat().st_size,
    )


# ── XML parsing ───────────────────────────────────────────────────────────────


def parse_xml_data(xml_content: bytes) -> dict:
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

    missing_fields = [k for k, v in raw.items() if v is None]
    if missing_fields:
        raise ValueError(f"Campos obligatorios ausentes en XML: {missing_fields}")

    serie, number = raw["full_id"].split("-")

    payment_means = root.find("cac:PaymentTerms/cbc:PaymentMeansID", NAMESPACES)
    is_advance = (
        payment_means is not None
        and payment_means.text is not None
        and payment_means.text.strip().lower() == "credito"
    )

    return {
        "serie": serie,
        "number": int(number),
        "currency": raw["currency"],
        "period": raw["issue_date"].replace("-", "")[:6],
        "total_amount": float(raw["total_amount"]),
        "issue_date": date.fromisoformat(raw["issue_date"]),
        "customer_ruc": raw["customer_ruc"],
        "customer_name": raw["customer_name"],
        "is_advance": is_advance,
    }


def parse_zip_invoice(zip_path: Path) -> dict:
    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"{zip_path.name} no es un ZIP válido")

    with zipfile.ZipFile(zip_path, "r") as z:
        xml_name = next((f for f in z.namelist() if f.lower().endswith(".xml")), None)
        if not xml_name:
            raise ValueError(f"No se encontró XML dentro de {zip_path.name}")
        return parse_xml_data(z.read(xml_name))


# ── Patrones de archivos ──────────────────────────────────────────────────────
#
# Tipos SUNAT (nombre oficial intacto) vs fehaciencia (renombrar con timestamp).
# Separar la responsabilidad de "qué guardar tal cual" vs "qué renombrar"
# hace el flujo más legible y fácil de extender.

SUNAT_TYPES = {
    DocumentType.INVOICE_ZIP,
    DocumentType.INVOICE_XML,
    DocumentType.INVOICE_PDF,
    DocumentType.DELIVERY_GUIDE_XML,
    DocumentType.CREDIT_NOTE_XML,
    DocumentType.CREDIT_NOTE_PDF,
    DocumentType.CREDIT_NOTE_ZIP,
}


def build_patterns(serie: str, number: int, ruc: str) -> dict[DocumentType, str]:
    return {
        DocumentType.INVOICE_PDF: rf"^PDF-DOC-{serie}-?{number}{ruc}\.pdf$",
        DocumentType.DELIVERY_GUIDE: rf"^{ruc}-09-.*\.pdf$",
        DocumentType.DELIVERY_GUIDE_XML: rf"^{ruc}-09-.*\.xml$",
        DocumentType.PURCHASE_ORDER: rf"^OC-{number}\.(pdf|jpg|jpeg|png)$",
        DocumentType.DELIVERY_GUIDE_SIGNED:  # antes SIGNED_SHIPPING_RECEIPT
        rf"^GF-{number}\.(pdf|jpg|jpeg|png)$",
        DocumentType.AGENCY_GUIDE:  # antes CARRIER_RECEIPT
        rf"^AG-{number}\.(pdf|jpg|jpeg|png)$",
        DocumentType.PAYMENT_VOUCHER:  # antes BANK_VOUCHER
        rf"^dp-{number}.*\.(pdf|jpg|jpeg|png)$",
        DocumentType.PHOTO: rf"^ft-{number}.*\.(jpg|jpeg|png|webp|heic)$",
        DocumentType.CREDIT_NOTE_ZIP: rf"^NOTA_CREDITO.*{serie}.*\.zip$",
        DocumentType.CREDIT_NOTE_PDF: rf"^PDF-NOTA_CREDITO.*\.pdf$",
        DocumentType.CREDIT_NOTE_XML: rf"^.*NOTA_CREDITO.*{serie}.*\.xml$",
    }


# ── Flujo principal ───────────────────────────────────────────────────────────


def main():
    RUC = "20610555536"
    VOUCHER_DIR = Path("/home/johneyder/Downloads/COMPROBANTES/2026/")
    invoice_regex = re.compile(rf"FACTURAE001-[0-9]{{4}}{RUC}\.zip", re.IGNORECASE)

    all_zips = list(VOUCHER_DIR.rglob("*.zip"))
    invoice_zips = [z for z in all_zips if invoice_regex.fullmatch(z.name)]

    print(f"🚀 {len(invoice_zips)} facturas encontradas para procesar.")

    with Session(engine) as session:
        for zip_path in invoice_zips:
            try:
                invoice_data = parse_zip_invoice(zip_path)
                serie = invoice_data["serie"]
                number = invoice_data["number"]
                issue_date: date = invoice_data["issue_date"]

                local_path = f"{invoice_data['period']}/VENTAS/{serie}-{number}"
                target_dir = STORAGE_PATH / local_path

                # 1. Registrar la factura
                invoice = SalesInvoice(
                    local_path=local_path,
                    period=invoice_data["period"],
                    serie=serie,
                    number=number,
                    issue_date=issue_date,
                    customer_ruc=invoice_data["customer_ruc"],
                    customer_name=invoice_data["customer_name"],
                    currency=invoice_data["currency"],
                    total_amount=invoice_data["total_amount"],
                    is_advance=invoice_data["is_advance"],
                )
                session.add(invoice)
                session.commit()
                session.refresh(invoice)

                # 2. Guardar y registrar el ZIP raíz de la factura
                stored = store_file(zip_path, target_dir, zip_path.name)
                session.add(
                    make_document(
                        invoice.id, DocumentType.INVOICE_ZIP, zip_path, stored
                    )
                )

                # 3. Buscar carpeta de adjuntos humanos
                month_name = MONTHS.get(issue_date.month)
                assert month_name, f"Mes inválido: {issue_date.month}"
                attachments_dir = VOUCHER_DIR / month_name / "VENTAS" / str(number)

                if not attachments_dir.exists():
                    print(
                        f"  ⚠️  Carpeta '{number}/' no encontrada — solo ZIP registrado."
                    )
                    session.commit()
                    continue

                files = [f.name for f in attachments_dir.iterdir() if f.is_file()]
                patterns = build_patterns(serie, number, RUC)

                # 4. Procesar cada tipo de documento
                for doc_type, pattern in patterns.items():
                    matches = find_all_by_pattern(files, pattern)

                    if not matches:
                        continue

                    # INVOICE_PDF: si hay 2 variantes (con/sin guion), usar solo la primera
                    if doc_type == DocumentType.INVOICE_PDF:
                        matches = matches[:1]

                    for filename in matches:
                        # Evita reprocesar el ZIP raíz si aparece dentro de la carpeta
                        if filename == zip_path.name:
                            continue

                        source = attachments_dir / filename

                        # Nombres SUNAT se conservan; fehaciencia se renombra para evitar colisiones
                        target_name = (
                            filename
                            if doc_type in SUNAT_TYPES
                            else generate_unique_filename(filename, doc_type)
                        )

                        stored = store_file(source, target_dir, target_name)
                        session.add(make_document(invoice.id, doc_type, source, stored))

                session.commit()
                print(f"  ✅ {serie}-{number:04d} procesada correctamente")

            except Exception as e:
                session.rollback()
                print(f"  ❌ Error en {zip_path.name}: {e}")


if __name__ == "__main__":
    main()
