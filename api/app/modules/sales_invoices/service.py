# app/sales_invoices/service.py
from sqlmodel import Session, select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from .model import SalesInvoice
from .schema import SalesInvoiceCreate, SalesInvoiceOut
from .serializer import serialize_invoice


class SaleInvoiceService:
    def __init__(self, session: Session):
        self.session = session

    def _base_query(self, q: str | None = None):
        query = (
            select(SalesInvoice)
            .options(selectinload(SalesInvoice.documents))
        )
        if q:
            search_pattern = f"%{q}%"
            query = query.where(
                or_(
                    SalesInvoice.invoice_id.like(search_pattern),
                    SalesInvoice.customer_ruc.like(search_pattern),
                    SalesInvoice.customer_name.like(search_pattern)
                )
            )
        return query.order_by(SalesInvoice.period.desc(), SalesInvoice.sequential_number.desc())

    def get_filtered_and_serialized(
        self,
        q: str | None = None,
        period: str | None = None,
        status: str | None = None,
    ) -> list[SalesInvoiceOut]:
        query = self._base_query(q)
        if period:
            query = query.where(SalesInvoice.period == period)

        invoices = self.session.exec(query).all()
        serialized = [serialize_invoice(inv) for inv in invoices]

        if status:
            serialized = [inv for inv in serialized if inv.status == status]

        return serialized

    def get_all(
        self,
        q: str | None = None,
        period: str | None = None,
        status: str | None = None,
    ) -> list[SalesInvoiceOut]:
        return self.get_filtered_and_serialized(q=q, period=period, status=status)

    def get_paginated(
        self,
        page: int,
        limit: int,
        q: str | None = None,
        period: str | None = None,
        status: str | None = None,
    ) -> tuple[list[SalesInvoiceOut], int]:
        all_matches = self.get_filtered_and_serialized(q=q, period=period, status=status)
        total = len(all_matches)
        
        offset = (page - 1) * limit
        paginated_slice = all_matches[offset : offset + limit]
        
        return paginated_slice, total

    def get_distinct_periods(self) -> list[str]:
        periods = self.session.exec(
            select(SalesInvoice.period)
            .distinct()
            .order_by(SalesInvoice.period.desc())
        ).all()
        return list(periods)

    def get_by_id(self, invoice_id: str) -> SalesInvoiceOut | None:
        invoice = self.session.exec(
            self._base_query().where(SalesInvoice.id == invoice_id)
        ).first()
        return serialize_invoice(invoice) if invoice else None

    def find_by_serie_and_number(self, serie: str, number: int):
        stqm = select(SalesInvoice).where(
            SalesInvoice.serie == serie, SalesInvoice.sequential_number == number
        )
        invoice = self.session.exec(stqm).first()

        if invoice is None:
            return None

        return serialize_invoice(invoice)

    def create(self, data: SalesInvoiceCreate) -> SalesInvoiceOut:
        invoice = SalesInvoice(**data.model_dump())
        self.session.add(invoice)
        self.session.commit()
        self.session.refresh(invoice)
        return serialize_invoice(invoice)
