from sqlmodel import Session, select, or_
from sqlalchemy.orm import selectinload
from .model import SalesInvoice
from app.modules.supporting_documents.model import SupportingDocument


class SaleInvoiceRepository:
    def __init__(self, session: Session):
        self.session = session

    def _base_query(self, q: str | None = None):
        query = select(SalesInvoice).options(selectinload(SalesInvoice.documents))  # type: ignore
        if q:
            search_pattern = f"%{q}%"
            query = query.where(
                or_(
                    SalesInvoice.document_id.like(search_pattern),  # type: ignore
                    SalesInvoice.customer_ruc.like(search_pattern),  # type: ignore
                    SalesInvoice.customer_name.like(search_pattern),  # type: ignore
                )
            )
        return query.order_by(
            SalesInvoice.period.desc(), SalesInvoice.sequential_number.desc()
        )

    def get_all(
        self, q: str | None = None, period: str | None = None
    ) -> list[SalesInvoice]:
        query = self._base_query(q)
        if period:
            query = query.where(SalesInvoice.period == period)
        return list(self.session.exec(query).all())

    def get_by_id(self, id: str) -> SalesInvoice | None:
        sqtm = (
            select(SalesInvoice)
            .where(SalesInvoice.id == id)
            .options(
                selectinload(SalesInvoice.credit_notes),  # type: ignore
                selectinload(SalesInvoice.delivery_notes),  # type: ignore
            )
        )
        return self.session.exec(sqtm).first()

    def get_by_document_id(self, document_id: str) -> SalesInvoice | None:
        return self.session.exec(
            select(SalesInvoice)
            .options(
                selectinload(SalesInvoice.documents),  # type: ignore
                selectinload(SalesInvoice.credit_notes),  # type: ignore
                selectinload(SalesInvoice.delivery_notes),  # type: ignore
            )  # type: ignore
            .where(SalesInvoice.document_id == document_id)
        ).first()

    def get_distinct_periods(self) -> list[str]:
        periods = self.session.exec(
            select(SalesInvoice.period).distinct().order_by(SalesInvoice.period.desc())
        ).all()
        return list(periods)

    def create(self, invoice: SalesInvoice) -> SalesInvoice:
        self.session.add(invoice)
        self.session.commit()
        self.session.refresh(invoice)
        return invoice

    def update(self, invoice: SalesInvoice, data_dict: dict) -> SalesInvoice:
        for key, value in data_dict.items():
            setattr(invoice, key, value)
        self.session.add(invoice)
        self.session.commit()
        self.session.refresh(invoice)
        return invoice

    def delete(self, invoice: SalesInvoice) -> None:
        self.session.delete(invoice)
        self.session.commit()

    def add_document(self, document: SupportingDocument) -> SupportingDocument:
        self.session.add(document)
        self.session.commit()
        self.session.refresh(document)
        return document
