import xml.etree.ElementTree as ET
from app.config import STORAGE_PATH
from .seed import get_text, find_all
from app.core.database import engine, Session
from app.modules.sales_invoices.model import SalesInvoice
from sqlmodel import select


def parse_xml_data(xml_content: bytes) -> tuple:
    root = ET.fromstring(xml_content)

    # Si el XML contiene el código de modalidad de traslado 02 (por agencia).
    agency_name = get_text(
        root, ".//cac:CarrierParty//cac:PartyLegalEntity//cbc:RegistrationName"
    )

    aditional_references = find_all(root, ".//cac:AdditionalDocumentReference/cbc:ID")

    return (agency_name, aditional_references)


def main():
    guides_path = list(STORAGE_PATH.rglob("20610555536-09*.xml"))
    with Session(engine) as session:
        for credit_note_path in guides_path:
            try:
                agency_name, aditional_references = parse_xml_data(
                    credit_note_path.read_bytes()
                )
                if agency_name is None or len(aditional_references) == 0:
                    continue

                for aditional_reference in aditional_references:
                    stmt = select(SalesInvoice).where(
                        SalesInvoice.serie == aditional_reference.split("-")[0],
                        SalesInvoice.sequential_number
                        == int(aditional_reference.split("-")[1]),
                    )

                    invoice = session.exec(stmt).first()

                    if invoice is None:
                        continue

                    invoice.is_agency_shipment = True

                    session.commit()

                    print(
                        f"  ✅ {invoice.serie}-{invoice.sequential_number:04d} procesada correctamente"
                    )
            except Exception as e:
                print(f"Error al procesar {credit_note_path}: {e}")


main()
