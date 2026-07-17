# app/sales_invoices/router.py
from fastapi import APIRouter, Depends, Response, UploadFile, File, Form

from .schema import SalesInvoiceCreate, SalesInvoiceOut, SalesInvoiceUpdate
from .service import SaleInvoiceService
from app.core.database import get_session
from app.core.auth import get_current_user

router = APIRouter(
    prefix="/sales-invoices",
    tags=["sales_invoices"],
    dependencies=[Depends(get_current_user)],
)


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
        invoices, total = service.get_paginated(
            page, limit, q=q, period=period, status=status
        )
        response.headers["X-Total-Count"] = str(total)
        response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"
        return invoices
    return service.get_all(q=q, period=period, status=status)


@router.get("/periods", response_model=list[str])
def list_periods(session=Depends(get_session)):
    return SaleInvoiceService(session).get_distinct_periods()


@router.get(
    "/{id}",
)
def get_invoice(id: str, session=Depends(get_session)):
    return SaleInvoiceService(session).get_by_id(id)


@router.get("/search/{document_id}", response_model=SalesInvoiceOut)
def find_invoice(document_id: str, session=Depends(get_session)):
    service = SaleInvoiceService(session)
    return service.find_by_serie_and_number(document_id)


# @router.put("/{id}", response_model=SalesInvoiceOut)
# def update_invoice(id: str, payload: SalesInvoiceUpdate, session=Depends(get_session)):
#     service = SaleInvoiceService(session)
#     return service.update(id, payload)
#
#
# @router.patch("/script/{document_id}", response_model=SalesInvoiceOut)
# def update_by_document_id(
#     document_id: str, payload: SalesInvoiceUpdate, session=Depends(get_session)
# ):
#     print("payload", payload)
#     service = SaleInvoiceService(session)
#     return service.update_by_document_id(document_id, payload)
#
#
@router.post("", status_code=201, response_model=SalesInvoiceOut)
def create_invoice(payload: SalesInvoiceCreate, session=Depends(get_session)):
    return SaleInvoiceService(session).create(payload)


@router.post("/create-from-zip", status_code=201)
async def create_invoice_with_zipfile(
    file: UploadFile = File(...), session=Depends(get_session)
):
    content = await file.read()
    return SaleInvoiceService(session).create_from_zip(content)


@router.post("/pdf/{invoice_id}", status_code=201)
async def insert_invoice_pdf_file(
    invoice_id: str, file: UploadFile = File(...), session=Depends(get_session)
):
    content = await file.read()
    return SaleInvoiceService(session).insert_pdf(invoice_id, content, file.filename)


#
#
# @router.delete("/{id}", status_code=204)
# def delete_invoice(id: str, session=Depends(get_session)):
#     service = SaleInvoiceService(session)
#     service.delete_sale_invoice(id)
#     return Response(status_code=204)
#
#
# @router.post("/upload")
# async def upload_file(
#     invoice_id: str = Form(...),
#     document_type: DocumentType = Form(...),
#     file: UploadFile = File(...),
#     session=Depends(get_session),
# ):
#     service = SaleInvoiceService(session)
#     document = await service.upload_file(invoice_id, document_type, file)
#     return {"document": document}
