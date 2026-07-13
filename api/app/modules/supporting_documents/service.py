from sqlmodel import Session
import os
from app.core.errors import NotFoundAppError
from app.config import STORAGE_PATH
from .model import SupportingDocument
from .schema import SupportingDocumentCreate, SupportingDocumentUpdate
from .repository import SupportingDocumentRepository


class SupportingDocumentService:
    def __init__(self, session: Session):
        self.repository = SupportingDocumentRepository(session)

    def get_all(self) -> list[SupportingDocument]:
        return self.repository.get_all()

    def get_by_id(self, document_id: str) -> SupportingDocument:
        doc = self.repository.get_by_id(document_id)
        if not doc:
            raise NotFoundAppError(f"Documento de soporte con id {document_id} no encontrado")
        return doc

    def create(self, data: SupportingDocumentCreate) -> SupportingDocument:
        document = SupportingDocument(**data.model_dump())
        return self.repository.create(document)

    def update(self, document_id: str, data: SupportingDocumentUpdate) -> SupportingDocument:
        doc = self.get_by_id(document_id)
        return self.repository.update(doc, data.model_dump(exclude_unset=True))

    def delete(self, document_id: str) -> None:
        doc = self.get_by_id(document_id)
        if doc.file_path:
            path = STORAGE_PATH / doc.file_path
            if path.exists() and path.is_file():
                os.remove(path)
        if doc.thumbnail_path:
            thumb_path = STORAGE_PATH / doc.thumbnail_path
            if thumb_path.exists() and thumb_path.is_file():
                os.remove(thumb_path)
        self.repository.delete(doc)
