from pathlib import Path
from datetime import datetime
import mimetypes
import magic

# import shutil
from app.modules.sales_invoices.types import DocumentType

SUNAT_TYPES = {
    DocumentType.INVOICE_ZIP,
    DocumentType.INVOICE_XML,
    DocumentType.INVOICE_PDF,
    DocumentType.DELIVERY_GUIDE_XML,
    DocumentType.CREDIT_NOTE_XML,
    DocumentType.CREDIT_NOTE_PDF,
    DocumentType.CREDIT_NOTE_ZIP,
    DocumentType.DELIVERY_GUIDE_PDF,
}


def generate_unique_filename(original_name: str, doc_type: DocumentType) -> str:
    if doc_type in SUNAT_TYPES:
        return original_name

    ext = Path(original_name).suffix
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"{doc_type.value.lower()}_{timestamp}{ext}"


def detect_mime_type(file: bytes) -> str:
    return magic.from_buffer(file, mime=True)


def store_file(source: bytes, target_dir: Path, target_name: str) -> Path:
    """Copia el archivo al directorio de destino y devuelve la ruta destino."""
    target_dir.mkdir(parents=True, exist_ok=True)
    destination = target_dir / target_name
    destination.write_bytes(source)
    # shutil.copy2(source, destination)
    return destination
