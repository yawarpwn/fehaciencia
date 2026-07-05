# app/sales_invoices/router.py
from fastapi import APIRouter, Depends, HTTPException
from .schema import SalesInvoiceCreate, SalesInvoiceOut
from .service import SaleInvoiceService
from app.core.database import get_session

router = APIRouter(prefix="/sales-invoices", tags=["sales_invoices"])


@router.get("", response_model=list[SalesInvoiceOut])
def list_invoices(session=Depends(get_session)):
    return SaleInvoiceService(session).get_all()


@router.get("/{invoice_id}", response_model=SalesInvoiceOut)
def get_invoice(invoice_id: str, session=Depends(get_session)):
    invoice = SaleInvoiceService(session).get_by_id(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return invoice


@router.post("", response_model=SalesInvoiceOut, status_code=201)
def create_invoice(payload: SalesInvoiceCreate, session=Depends(get_session)):
    return SaleInvoiceService(session).create(payload)
