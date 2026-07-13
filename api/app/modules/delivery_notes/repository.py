from sqlmodel import Session, select
from .model import DeliveryNote, DeliveryNoteReference


class DeliveryNoteRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[DeliveryNote]:
        return list(self.session.exec(select(DeliveryNote)).all())

    def get_by_id(self, delivery_note_id: str) -> DeliveryNote | None:
        return self.session.get(DeliveryNote, delivery_note_id)

    def get_by_document_id(self, document_id: str) -> DeliveryNote | None:
        statement = select(DeliveryNote).where(DeliveryNote.document_id == document_id)
        return self.session.exec(statement).first()

    def get_by_delivery_note_id(self, document_id: str) -> DeliveryNote | None:
        return self.session.exec(
            select(DeliveryNote).where(DeliveryNote.document_id == document_id)
        ).first()

    def create(self, delivery_note: DeliveryNote) -> DeliveryNote:
        self.session.add(delivery_note)
        self.session.commit()
        self.session.refresh(delivery_note)
        return delivery_note

    def update(self, delivery_note: DeliveryNote, data_dict: dict) -> DeliveryNote:
        for key, value in data_dict.items():
            setattr(delivery_note, key, value)
        self.session.add(delivery_note)
        self.session.commit()
        self.session.refresh(delivery_note)
        return delivery_note

    def delete(self, delivery_note: DeliveryNote) -> None:
        self.session.delete(delivery_note)
        self.session.commit()


class DeliveryNoteReferenceRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, reference: DeliveryNoteReference) -> DeliveryNoteReference:
        self.session.add(reference)
        self.session.commit()
        self.session.refresh(reference)
        return reference
