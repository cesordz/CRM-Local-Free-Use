from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import NoteCreate
from app import services

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/clients/{client_id}/notes", response_class=HTMLResponse)
def add_note(
    request: Request,
    client_id: int,
    content: str = Form(""),
    db: Session = Depends(get_db)
):
    client = services.get_client_by_id(db, client_id)
    if not client:
        return RedirectResponse(
            url="/clients?error=Cliente+no+encontrado",
            status_code=status.HTTP_303_SEE_OTHER
        )

    errors = {}
    try:
        validated_note = NoteCreate(content=content)
        services.create_note(db, client_id, validated_note)
        return RedirectResponse(
            url=f"/clients/{client_id}?msg=Nota+agregada+exitosamente",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except ValidationError as ve:
        for err in ve.errors():
            errors["content"] = err["msg"].replace("Value error, ", "")
    except Exception as e:
        errors["content"] = f"Error al guardar la nota: {str(e)}"

    return templates.TemplateResponse(
        request=request,
        name="clients/detail.html",
        context={
            "client": client,
            "errors": errors,
            "note_content": content
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@router.post("/clients/{client_id}/notes/{note_id}/delete")
def delete_note(
    client_id: int,
    note_id: int,
    db: Session = Depends(get_db)
):
    try:
        services.delete_note(db, note_id)
        return RedirectResponse(
            url=f"/clients/{client_id}?msg=Nota+eliminada+exitosamente",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except services.NoteNotFoundError:
        return RedirectResponse(
            url=f"/clients/{client_id}?error=Nota+no+encontrada",
            status_code=status.HTTP_303_SEE_OTHER
        )
