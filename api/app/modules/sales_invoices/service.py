from sqlmodel import Session
from .model import SalesInvoice, SupportingDocument
from sqlalchemy.orm import selectinload
from .schema import CreateSalesInvoice
from sqlmodel import select


class SaleInvoiceService:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self):
        statement = select(SalesInvoice).options(selectinload(SalesInvoice.documents))
        return self.session.exec(statement).all()

    def create(self, data: CreateSalesInvoice) -> SalesInvoice:

        # database
        invoice = SalesInvoice(**data.model_dump())

        self.session.add(invoice)
        self.session.commit()
        self.session.refresh(invoice)
        return invoice
