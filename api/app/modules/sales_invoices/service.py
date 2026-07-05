# app/sales_invoices/service.py
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from .model import SalesInvoice
from .schema import SalesInvoiceCreate, SalesInvoiceOut
from .serializer import serialize_invoice


class SaleInvoiceService:
    def __init__(self, session: Session):
        self.session = session

    def _base_query(self):
        return (
            select(SalesInvoice)
            .options(selectinload(SalesInvoice.documents))
            .order_by(SalesInvoice.period.desc(), SalesInvoice.number.desc())
        )

    def get_all(self) -> list[SalesInvoiceOut]:
        invoices = self.session.exec(self._base_query()).all()
        return [serialize_invoice(inv) for inv in invoices]

    def get_by_id(self, invoice_id: str) -> SalesInvoiceOut | None:
        invoice = self.session.exec(
            self._base_query().where(SalesInvoice.id == invoice_id)
        ).first()
        return serialize_invoice(invoice) if invoice else None

    def find_by_serie_and_number(self, serie: str, number: int):
        stqm = select(SalesInvoice).where(
            SalesInvoice.serie == serie, SalesInvoice.number == number
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
