import zipfile
import shutil
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, date
from sqlmodel import Session

from app.core.database import engine
from app.sales_invoices.model import SalesInvoice, SupportingDocument, AssetType
from app.config import STORAGE_PATH

NAMESPACES = {
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
}


def get_text(root: ET.Element, tag: str) -> str | None:
    node = root.find(tag, NAMESPACES)
    return node.text.strip() if node is not None and node.text else None


def find_all_by_pattern(files: list[str], pattern_str: str) -> list[str]:
    """Busca TODOS los archivos que hagan match con la expresión regular (Case Insensitive)."""
    regex = re.compile(pattern_str, re.I)
    return [f for f in files if regex.match(f)]


def generate_unique_filename(original_name: str, asset_type: AssetType) -> str:
    """Genera un nombre único con timestamp preciso para evitar superposiciones en el almacenamiento."""
    ext = Path(original_name).suffix
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"{asset_type.value.lower()}_{timestamp}{ext}"


def parse_xml_data(xml_content: bytes) -> dict:
    root = ET.fromstring(xml_content)

    xml_mapping = {
        "full_id": "cbc:ID",
        "issue_date": "cbc:IssueDate",
        "customer_ruc": "cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID",
        "customer_name": "cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName",
        "currency": "cbc:DocumentCurrencyCode",
        "total_amount": "cac:LegalMonetaryTotal/cbc:PayableAmount",
    }

    raw_data = {key: get_text(root, path) for key, path in xml_mapping.items()}

    if not all(raw_data.values()):
        missing = [k for k, v in raw_data.items() if v is None]
        raise ValueError(f"Campos obligatorios ausentes en el XML: {missing}")

    assert raw_data["full_id"] is not None
    assert raw_data["issue_date"] is not None

    serie, number = raw_data["full_id"].split("-")

    payment_means = root.find("cac:PaymentTerms/cbc:PaymentMeansID", NAMESPACES)
    is_credit = (
        1
        if payment_means is not None and payment_means.text.strip().lower() == "credito"
        else 0
    )

    return {
        "serie": serie,
        "number": int(number),
        "currency": raw_data["currency"],
        "period": raw_data["issue_date"].replace("-", "")[:6],
        "total_amount": float(raw_data["total_amount"]),
        "issue_date": date.fromisoformat(raw_data["issue_date"]),
        "customer_ruc": raw_data["customer_ruc"],
        "customer_name": raw_data["customer_name"],
        "is_credit": is_credit,
    }


def process_zip_invoice(zip_path: Path) -> dict:
    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"❌ {zip_path.name} no es un ZIP válido")

    with zipfile.ZipFile(zip_path, "r") as z:
        xml_file_name = next(
            (f for f in z.namelist() if f.lower().endswith(".xml")), None
        )
        if not xml_file_name:
            raise ValueError(f"❌ No se encontró archivo XML dentro de {zip_path.name}")

        xml_content = z.read(xml_file_name)
        return parse_xml_data(xml_content)


def storage_file(file_path: Path, target_dir: Path, unique_name: str) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    destination = target_dir / unique_name
    shutil.copy2(file_path, destination)
    return destination


# --- 3. Flujo Ejecutable Principal ---
#
MOUNTS = {
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


def main():
    import uuid

    VOUCHER_DIR = Path("/home/johneyder/Downloads/COMPROBANTES/2026/")
    invoice_regex = re.compile(r"FACTURAE001-[0-9]{4}20610555536.zip", re.IGNORECASE)

    zips_path = list(VOUCHER_DIR.rglob("*.zip"))
    invoices_path = [
        invoice for invoice in zips_path if invoice_regex.fullmatch(invoice.name)
    ]

    invoices_path = invoices_path
    print(f"🚀 Se encontraron {len(invoices_path)} facturas potenciales para procesar.")

    with Session(engine) as session:
        for invoice_path in invoices_path:  # Limitado a 2 para pruebas iniciales
            try:
                # 1. Procesar XML principal de la Factura desde el ZIP
                invoice_data = process_zip_invoice(invoice_path)

                serie = invoice_data["serie"]
                number = invoice_data["number"]
                RUC = "20610555536"
                issue_date = invoice_data["issue_date"]

                local_path = f"{invoice_data['period']}/VENTAS/{serie}-{number}"
                target_storage_dir = STORAGE_PATH / local_path

                # 2. Registrar Factura (SalesInvoice)
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
                    is_credit=invoice_data["is_credit"],
                )
                session.add(invoice)
                session.commit()
                session.refresh(invoice)

                month = MOUNTS.get(issue_date.month)
                assert month is not None
                # 3. Buscar la carpeta correlativa de adjuntos humanos
                folder = VOUCHER_DIR / month / "VENTAS" / str(number)

                print("folder", folder)
                if not folder.exists():
                    print(
                        f"⚠️ Carpeta de adjuntos '{number}/' no encontrada. Saltando escaneo secundario."
                    )
                    continue

                files = [f.name for f in folder.iterdir() if f.is_file()]

                document_patterns = {
                    AssetType.INVOICE_PDF: rf"^PDF-DOC-{serie}-?{number}{RUC}\.pdf$",
                    # Guías de Remisión de SUNAT discriminadas
                    AssetType.DELIVERY_GUIDE_PDF: rf"^{RUC}-09-.*\.pdf$",
                    AssetType.DELIVERY_GUIDE_XML: rf"^{RUC}-09-.*\.xml$",
                    AssetType.PURCHASE_ORDER: rf"^OC-{number}\.(pdf|jpg|jpeg|png)$",
                    AssetType.SIGNED_SHIPPING_RECEIPT: rf"^GF-{number}\.(pdf|jpg|jpeg|png)$",
                    AssetType.BANK_VOUCHER: rf"^dp-{number}.*\.(pdf|jpg|jpeg|png)$",
                    AssetType.PHOTO: rf"^ft-{number}.*\.(pdf|jpg|jpeg|png)$",
                    # Notas de Crédito discriminadas con precisión según tu estructura
                    AssetType.CREDIT_NOTE_ZIP: rf"^NOTA_CREDITO.*{serie}.*\.zip$",
                    AssetType.CREDIT_NOTE_PDF: rf"^PDF-NOTA_CREDITO.*\.pdf$",
                    AssetType.CREDIT_NOTE_XML: rf"^.*NOTA_CREDITO.*{serie}.*\.xml$",  # Por si extraes el XML
                }

                # Guardar el ZIP de la factura que originó el proceso
                storage_file(invoice_path, target_storage_dir, invoice_path.name)
                session.add(
                    SupportingDocument(
                        id=str(uuid.uuid4()),
                        invoice_id=invoice.id,
                        document_type=AssetType.INVOICE_ZIP,
                        file_name=invoice_path.name,
                    )
                )

                # 4. Iterar y procesar todos los adjuntos encontrados de forma limpia
                for asset_type, pattern in document_patterns.items():
                    matched_files = find_all_by_pattern(files, pattern)

                    # Si no encontró ningún archivo para este patrón, saltamos al siguiente
                    if not matched_files:
                        continue

                    # Si encuentra 2 versiones del PDF de la factura (con o sin guion), nos quedamos SOLO con la primera
                    if asset_type in [AssetType.INVOICE_PDF]:
                        matched_files = [matched_files[0]]

                    for filename in matched_files:
                        # Prevenir volver a mover el ZIP raíz si está dentro de la misma carpeta
                        if filename == invoice_path.name:
                            continue

                        if asset_type in [
                            AssetType.INVOICE_ZIP,
                            AssetType.INVOICE_XML,
                            AssetType.INVOICE_PDF,
                            AssetType.DELIVERY_GUIDE_PDF,
                            AssetType.DELIVERY_GUIDE_XML,
                            AssetType.CREDIT_NOTE_XML,
                            AssetType.CREDIT_NOTE_PDF,
                            AssetType.CREDIT_NOTE_ZIP,
                        ]:
                            # Conserva su nombre oficial tal cual vino de SUNAT
                            unique_name = filename
                        else:
                            # Evita que las fotos o vouchers "chancen" a otros
                            unique_name = generate_unique_filename(filename, asset_type)

                        # Guardado físico en destino ordenado
                        storage_file(folder / filename, target_storage_dir, unique_name)

                        # Registro indexado en base de datos
                        doc = SupportingDocument(
                            id=str(uuid.uuid4()),
                            invoice_id=invoice.id,
                            document_type=asset_type,
                            file_name=unique_name,
                        )
                        session.add(doc)

                session.commit()
                print(f"✅ Transacción completa para Comprobante: {serie}-{number}")

            except Exception as e:
                session.rollback()
                print(f"❌ Error crítico procesando archivo {invoice_path.name}: {e}")


if __name__ == "__main__":
    main()
