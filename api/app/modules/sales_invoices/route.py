# app/sales_invoices/router.py
from fastapi import APIRouter, Depends, HTTPException, Response
from .schema import SalesInvoiceCreate, SalesInvoiceOut
from .service import SaleInvoiceService
from app.core.database import get_session

router = APIRouter(prefix="/sales-invoices", tags=["sales_invoices"])


@router.get("", response_model=list[SalesInvoiceOut])
def list_invoices(
    response: Response,
    page: int | None = None,
    limit: int | None = None,
    q: str | None = None,
    period: str | None = None,
    status: str | None = None,
    session=Depends(get_session),
):
    service = SaleInvoiceService(session)
    if page is not None and limit is not None:
        invoices, total = service.get_paginated(page, limit, q=q, period=period, status=status)
        response.headers["X-Total-Count"] = str(total)
        response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"
        return invoices
    return service.get_all(q=q, period=period, status=status)


@router.get("/periods", response_model=list[str])
def list_periods(session=Depends(get_session)):
    return SaleInvoiceService(session).get_distinct_periods()


@router.get("/{invoice_id}", response_model=SalesInvoiceOut)
def get_invoice(invoice_id: str, session=Depends(get_session)):
    invoice = SaleInvoiceService(session).get_by_id(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return invoice


@router.get("/search/{invoice_code}", response_model=SalesInvoiceOut)
def find_invoice(invoice_code: str, session=Depends(get_session)):
    serie, number = invoice_code.upper().split("-")
    service = SaleInvoiceService(session)
    invoice = service.find_by_serie_and_number(serie, int(number))
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return invoice


@router.post("", response_model=SalesInvoiceOut, status_code=201)
def create_invoice(payload: SalesInvoiceCreate, session=Depends(get_session)):
    return SaleInvoiceService(session).create(payload)
