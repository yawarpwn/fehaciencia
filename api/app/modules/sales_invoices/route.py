from fastapi import APIRouter, Depends
from .schema import CreateSalesInvoice, SalesInvoiceResponse
from .service import SaleInvoiceService
from app.core.database import get_session

router = APIRouter(prefix="/sales-invoices", tags=["sales_invoices"])


@router.get("", response_model=list[SalesInvoiceResponse])
def get_sales_invoices(session=Depends(get_session)):
    service = SaleInvoiceService(session)
    return service.get_all()


@router.post("", response_model=SalesInvoiceResponse)
def create_sales_invoice(payload: CreateSalesInvoice, session=Depends(get_session)):
    service = SaleInvoiceService(session)
    invoice = service.create(payload)
    return invoice
