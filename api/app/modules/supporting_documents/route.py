from fastapi import APIRouter, Depends, Response, UploadFile, File, Form
from app.core.database import get_session
from app.core.auth import get_current_user
from app.core.types import DocumentType
from .schema import (
    SupportingDocumentCreate,
    SupportingDocumentUpdate,
    SupportingDocumentOut,
)
from .service import SupportingDocumentService

router = APIRouter(
    prefix="/supporting-documents",
    tags=["supporting_documents"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[SupportingDocumentOut])
def list_documents(session=Depends(get_session)):
    return SupportingDocumentService(session).get_all()


@router.get("/{document_id}", response_model=SupportingDocumentOut)
def get_document(document_id: str, session=Depends(get_session)):
    return SupportingDocumentService(session).get_by_id(document_id)


@router.post("", status_code=201)
async def create_document(
    file: UploadFile = File(...),
    document_type: DocumentType = Form(...),
    invoice_id: str = Form(...),
    session=Depends(get_session),
):

    content = await file.read()
    return SupportingDocumentService(session).create(
        content=content,
        document_type=document_type,
        invoice_id=invoice_id,
        filename=file.filename,
    )


@router.put("/{document_id}", response_model=SupportingDocumentOut)
def update_document(
    document_id: str, payload: SupportingDocumentUpdate, session=Depends(get_session)
):
    return SupportingDocumentService(session).update(document_id, payload)


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: str, session=Depends(get_session)):
    SupportingDocumentService(session).delete(document_id)
    return Response(status_code=204)
