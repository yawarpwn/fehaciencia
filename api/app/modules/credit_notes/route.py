from fastapi import APIRouter, Depends, Response, UploadFile, File
from app.core.database import get_session
from app.core.auth import get_current_user
from .schema import CreditNoteCreate, CreditNoteUpdate, CreditNoteOut
from .service import CreditNoteService

router = APIRouter(
    prefix="/credit-notes",
    tags=["credit_notes"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[CreditNoteOut])
def list_credit_notes(session=Depends(get_session)):
    return CreditNoteService(session).get_all()


@router.get("/{id}", response_model=CreditNoteOut)
def get_credit_note(id: str, session=Depends(get_session)):
    return CreditNoteService(session).get_by_id(id)


@router.get("/search/{credit_note_id}", response_model=CreditNoteOut)
def search_credit_note(credit_note_id: str, session=Depends(get_session)):
    return CreditNoteService(session).get_by_credit_note_id(credit_note_id)


@router.post("", response_model=CreditNoteOut, status_code=201)
def create_credit_note(payload: CreditNoteCreate, session=Depends(get_session)):
    return CreditNoteService(session).create(payload)


@router.post("/create-from-zip", status_code=201)
async def create_invoice_with_zipfile(
    file: UploadFile = File(...), session=Depends(get_session)
):
    content = await file.read()
    return CreditNoteService(session).create_from_zip(content, file.filename)


@router.post("/pdf/{id}", status_code=201)
async def insert_invoice_pdf_file(
    id: str, file: UploadFile = File(...), session=Depends(get_session)
):
    content = await file.read()
    return CreditNoteService(session).insert_pdf(id, content, file.filename)


@router.put("/{credit_note_id}", response_model=CreditNoteOut)
def update_credit_note(
    credit_note_id: str, payload: CreditNoteUpdate, session=Depends(get_session)
):
    return CreditNoteService(session).update(credit_note_id, payload)


@router.delete("/{credit_note_id}", status_code=204)
def delete_credit_note(credit_note_id: str, session=Depends(get_session)):
    CreditNoteService(session).delete(credit_note_id)
    return Response(status_code=204)
