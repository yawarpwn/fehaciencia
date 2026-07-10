from sqlmodel import Session, select, or_
from sqlalchemy.orm import selectinload
from .model import SalesInvoice, SupportingDocument


class SaleInvoiceRepository:
    def __init__(self, session: Session):
        self.session = session

    def _base_query(self, q: str | None = None):
        query = select(SalesInvoice).options(selectinload(SalesInvoice.documents))
        if q:
            search_pattern = f"%{q}%"
            query = query.where(
                or_(
                    SalesInvoice.invoice_id.like(search_pattern),
                    SalesInvoice.customer_ruc.like(search_pattern),
                    SalesInvoice.customer_name.like(search_pattern),
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

    def get_by_id(self, invoice_id: str) -> SalesInvoice | None:
        return self.session.exec(
            select(SalesInvoice)
            .options(selectinload(SalesInvoice.documents))
            .where(SalesInvoice.id == invoice_id)
        ).first()

    def get_by_invoice_id(self, invoice_id: str) -> SalesInvoice | None:
        return self.session.exec(
            select(SalesInvoice)
            .options(selectinload(SalesInvoice.documents))
            .where(SalesInvoice.invoice_id == invoice_id)
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
