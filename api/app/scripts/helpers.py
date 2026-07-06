import xml.etree.ElementTree as ET
import re
from pathlib import Path
import mimetypes
from datetime import datetime
import shutil
from app.config import STORAGE_PATH
from app.core.utils import thumbnails
from app.core.utils.thumbnails import generate_thumbnail
from app.modules.sales_invoices.model import (
    SalesInvoice,
    SupportingDocument,
    DocumentType,
)

NAMESPACES = {
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
}


def get_text(root: ET.Element, tag: str) -> str | None:
    node = root.find(tag, NAMESPACES)
    return node.text.strip() if node is not None and node.text else None


def find_all(root: ET.Element, tag: str) -> list[str]:
    node = root.findall(tag, NAMESPACES)
    return [n.text.strip() for n in node]


def is_prepayment_invoice(root) -> bool:
    invoice_type = root.find("cbc:InvoiceTypeCode", NAMESPACES)

    return invoice_type is not None and invoice_type.get("listID") in {"0104", "0204"}


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
    local_path: str | None,
) -> SupportingDocument:
    """Construye un SupportingDocument con todos los campos requeridos."""
    relative_path = stored_path.relative_to(STORAGE_PATH)
    mime_type = detect_mime_type(source_path)

    thumbnail_path = None

    if (
        mime_type.endswith("jpeg")
        or mime_type.endswith("jpg")
        or mime_type.endswith("png")
        or mime_type.endswith("webp")
        or mime_type.endswith("heic")
    ) and local_path is not None:
        thumbnail_path_name = generate_thumbnail(source_path, STORAGE_PATH / local_path)
        thumbnail_path = relative_path.parent / thumbnail_path_name

    return SupportingDocument(
        invoice_id=invoice_id,
        document_type=doc_type,
        file_name=stored_path.name,
        file_path=str(relative_path),  # relativo a STORAGE_PATH
        mime_type=mime_type,
        file_size=source_path.stat().st_size,
        thumbnail_path=str(thumbnail_path) if thumbnail_path is not None else None,
    )
