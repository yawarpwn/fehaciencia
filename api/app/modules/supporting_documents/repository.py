from sqlmodel import Session, select
from .model import SupportingDocument


class SupportingDocumentRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[SupportingDocument]:
        return list(self.session.exec(select(SupportingDocument)).all())

    def get_by_id(self, document_id: str) -> SupportingDocument | None:
        return self.session.get(SupportingDocument, document_id)

    def get_by_invoice_id(self, invoice_id: str) -> list[SupportingDocument]:
        return list(
            self.session.exec(
                select(SupportingDocument).where(SupportingDocument.invoice_id == invoice_id)
            ).all()
        )

    def create(self, document: SupportingDocument) -> SupportingDocument:
        self.session.add(document)
        self.session.commit()
        self.session.refresh(document)
        return document

    def update(self, document: SupportingDocument, data_dict: dict) -> SupportingDocument:
        for key, value in data_dict.items():
            setattr(document, key, value)
        self.session.add(document)
        self.session.commit()
        self.session.refresh(document)
        return document

    def delete(self, document: SupportingDocument) -> None:
        self.session.delete(document)
        self.session.commit()
