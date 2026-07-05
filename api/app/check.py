from operator import inv
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from app.config import STORAGE_PATH
from .seed import get_text
from app.core.database import engine, Session
from app.modules.sales_invoices.model import SalesInvoice
from sqlmodel import select

NAMESPACES = {
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
}


def parse_xml_data(xml_content: bytes) -> dict:
    root = ET.fromstring(xml_content)

    id = get_text(root, "cbc:ID")
    billing_reference = get_text(
        root, "cac:BillingReference/cac:InvoiceDocumentReference/cbc:ID"
    )
    assert billing_reference is not None
    serie, number = billing_reference.split("-")

    return {
        "serie": serie.strip(),
        "number": int(number.strip()),
    }


def parse_zip_invoice(zip_path: Path) -> dict:
    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"{zip_path.name} no es un ZIP válido")

    with zipfile.ZipFile(zip_path, "r") as z:
        xml_name = next((f for f in z.namelist() if f.lower().endswith(".xml")), None)
        if not xml_name:
            raise ValueError(f"No se encontró XML dentro de {zip_path.name}")
        return parse_xml_data(z.read(xml_name))


def main():
    credit_note_paths = list(STORAGE_PATH.rglob("NOTA_CREDITO*.zip"))
    with Session(engine) as session:
        for credit_note_path in credit_note_paths:
            try:
                data = parse_zip_invoice(credit_note_path)

                stmt = select(SalesInvoice).where(
                    SalesInvoice.serie == data["serie"],
                    SalesInvoice.number == data["number"],
                )

                invoice = session.exec(stmt).first()

                if invoice is None:
                    continue

                invoice.is_voided = True

                session.commit()

                print(
                    f"  ✅ {data['serie']}-{data['number']:04d} procesada correctamente"
                )
            except Exception as e:
                print(f"Error al procesar {credit_note_path}: {e}")


main()
