from app.modules.credit_notes.schema import CreditNoteOut
from app.modules.credit_notes.model import CreditNote
from app.core.utils import get_file_url

CATALOGO_09_NOTA_CREDITO = {
    "01": {
        "descripcion": "Anulación de la operación",
        "tipo": "TOTAL",
    },
    "02": {
        "descripcion": "Anulación por error en el RUC",
        "tipo": "TOTAL",
    },
    "03": {
        "descripcion": "Corrección por error en la descripción",
        "tipo": "PARCIAL",
    },
    "04": {
        "descripcion": "Descuento global",
        "tipo": "PARCIAL",
    },
    "05": {
        "descripcion": "Descuento por ítem",
        "tipo": "PARCIAL",
    },
    "06": {
        "descripcion": "Devolución total",
        "tipo": "TOTAL",
    },
    "07": {
        "descripcion": "Devolución por ítem",
        "tipo": "PARCIAL",
    },
    "08": {
        "descripcion": "Bonificación",
        "tipo": "PARCIAL",
    },
    "09": {
        "descripcion": "Disminución en el valor",
        "tipo": "PARCIAL",
    },
    "10": {
        "descripcion": "Otros conceptos",
        "tipo": "INDETERMINADO",  # revisar cbc:Description para decidir
    },
    "11": {
        "descripcion": "Ajustes de operaciones de exportación",
        "tipo": "PARCIAL",
    },
    "12": {
        "descripcion": "Ajustes afectos al IVAP",
        "tipo": "PARCIAL",
    },
    "13": {
        "descripcion": "Ajuste - Montos y/o fechas de pago",
        "tipo": "PARCIAL",
    },
}


def determinar_tipo_nota(response_code: str, description: str | None = None) -> str:
    info = CATALOGO_09_NOTA_CREDITO.get(response_code)
    if info is None:
        return "DESCONOCIDO"
    if info["tipo"] == "INDETERMINADO":
        # Aquí puedes aplicar heurística adicional con `description`
        # o comparar montos contra la factura referenciada
        return "PARCIAL"  # o la regla que definas para el código 10
    return info["tipo"]


# CODIGOS_TOTAL = {"01", "02", "06"}  # anulación / devolución total
# CODIGOS_PARCIAL = {"03", "04", "05", "07", "08", "09", "11", "12"}
#
# if response_code in CODIGOS_TOTAL:
#     tipo_nota = "TOTAL"
# elif response_code in CODIGOS_PARCIAL:
#     tipo_nota = "PARCIAL"
# else:
#     tipo_nota = "INDETERMINADO"


def serialize_credit_note(doc: CreditNote) -> CreditNoteOut:
    return CreditNoteOut(
        id=doc.id,
        invoice_id=doc.invoice_id,
        document_id=doc.document_id,
        issue_date=doc.issue_date,
        pdf_file_url=get_file_url(doc.pdf_file_path) if doc.pdf_file_path else None,
        xml_file_url=get_file_url(doc.xml_file_path),
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )
