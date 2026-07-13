from sqlmodel import Session, select
from .model import CreditNote


class CreditNoteRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[CreditNote]:
        return list(self.session.exec(select(CreditNote)).all())

    def get_by_id(self, credit_note_id: str) -> CreditNote | None:
        return self.session.get(CreditNote, credit_note_id)

    def get_by_invoice_id(self, invoice_id: str) -> list[CreditNote]:
        return list(
            self.session.exec(
                select(CreditNote).where(CreditNote.invoice_id == invoice_id)
            ).all()
        )

    def get_by_credit_note_id(self, credit_note_id: str) -> CreditNote | None:
        stmt = select(CreditNote).where(CreditNote.credit_note_id == credit_note_id)
        return self.session.exec(stmt).first()

    def create(self, credit_note: CreditNote) -> CreditNote:
        self.session.add(credit_note)
        self.session.commit()
        self.session.refresh(credit_note)
        return credit_note

    def update(self, credit_note: CreditNote, data_dict: dict) -> CreditNote:
        for key, value in data_dict.items():
            setattr(credit_note, key, value)
        self.session.add(credit_note)
        self.session.commit()
        self.session.refresh(credit_note)
        return credit_note

    def delete(self, credit_note: CreditNote) -> None:
        self.session.delete(credit_note)
        self.session.commit()
