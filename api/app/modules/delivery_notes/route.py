from fastapi import APIRouter, Depends, Response, UploadFile, File
from app.core.database import get_session
from app.core.auth import get_current_user
from .schema import DeliveryNoteCreate, DeliveryNoteUpdate, DeliveryNoteOut
from .service import DeliveryNoteService

router = APIRouter(
    prefix="/delivery-notes",
    tags=["delivery_notes"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[DeliveryNoteOut])
def list_delivery_notes(session=Depends(get_session)):
    return DeliveryNoteService(session).get_all()


@router.get("/{delivery_note_id}", response_model=DeliveryNoteOut)
def get_delivery_note(delivery_note_id: str, session=Depends(get_session)):
    return DeliveryNoteService(session).get_by_id(delivery_note_id)


@router.get("/search/{document_id}")
def search_delivery_note(document_id: str, session=Depends(get_session)):
    return DeliveryNoteService(session).get_by_document_id(document_id)


@router.post("", response_model=DeliveryNoteOut, status_code=201)
def create_delivery_note(payload: DeliveryNoteCreate, session=Depends(get_session)):
    return DeliveryNoteService(session).create(payload)


@router.post("/create-from-xml", status_code=201)
async def create_delivery_note_from_xml(
    file: UploadFile = File(...), session=Depends(get_session)
):

    content = await file.read()
    return DeliveryNoteService(session).create_from_xml(content, file.filename)


@router.post("/pdf/{id}", status_code=201)
async def insert_invoice_pdf_file(
    id: str, file: UploadFile = File(...), session=Depends(get_session)
):
    content = await file.read()
    return DeliveryNoteService(session).insert_pdf(id, content, file.filename)


@router.put("/{delivery_note_id}", response_model=DeliveryNoteOut)
def update_delivery_note(
    delivery_note_id: str, payload: DeliveryNoteUpdate, session=Depends(get_session)
):
    return DeliveryNoteService(session).update(delivery_note_id, payload)


@router.delete("/{delivery_note_id}", status_code=204)
def delete_delivery_note(delivery_note_id: str, session=Depends(get_session)):
    DeliveryNoteService(session).delete(delivery_note_id)
    return Response(status_code=204)
