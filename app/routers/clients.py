from typing import Optional
from fastapi import APIRouter, Depends, Request, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ClientCreate, ClientUpdate
from app import services

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def root_redirect():
    return RedirectResponse(url="/clients", status_code=status.HTTP_302_FOUND)


@router.get("/clients", response_class=HTMLResponse)
def list_clients(
    request: Request,
    q: Optional[str] = None,
    msg: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db)
):
    clients = services.get_clients(db, search=q)
    return templates.TemplateResponse(
        request=request,
        name="clients/list.html",
        context={
            "clients": clients,
            "search_query": q or "",
            "success_message": msg,
            "error_message": error
        }
    )


@router.get("/clients/new", response_class=HTMLResponse)
def new_client_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="clients/form.html",
        context={
            "action": "create",
            "client": None,
            "form_data": {},
            "errors": {}
        }
    )


@router.post("/clients/new", response_class=HTMLResponse)
def create_client(
    request: Request,
    name: str = Form(""),
    email: str = Form(""),
    phone: str = Form(""),
    company: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    form_data = {
        "name": name,
        "email": email,
        "phone": phone,
        "company": company or ""
    }
    errors = {}

    try:
        validated_data = ClientCreate(
            name=name,
            email=email,
            phone=phone,
            company=company
        )
        new_client = services.create_client(db, validated_data)
        return RedirectResponse(
            url=f"/clients/{new_client.id}?msg=Cliente+creado+con+%C3%A9xito",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except ValidationError as ve:
        for err in ve.errors():
            field = str(err["loc"][0])
            errors[field] = err["msg"].replace("Value error, ", "")
    except services.EmailAlreadyExistsError as ee:
        errors["email"] = str(ee)

    return templates.TemplateResponse(
        request=request,
        name="clients/form.html",
        context={
            "action": "create",
            "client": None,
            "form_data": form_data,
            "errors": errors
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@router.get("/clients/{client_id}", response_class=HTMLResponse)
def client_detail(
    request: Request,
    client_id: int,
    msg: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db)
):
    client = services.get_client_by_id(db, client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    return templates.TemplateResponse(
        request=request,
        name="clients/detail.html",
        context={
            "client": client,
            "success_message": msg,
            "error_message": error,
            "errors": {}
        }
    )


@router.get("/clients/{client_id}/edit", response_class=HTMLResponse)
def edit_client_form(
    request: Request,
    client_id: int,
    db: Session = Depends(get_db)
):
    client = services.get_client_by_id(db, client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    form_data = {
        "name": client.name,
        "email": client.email,
        "phone": client.phone,
        "company": client.company or ""
    }

    return templates.TemplateResponse(
        request=request,
        name="clients/form.html",
        context={
            "action": "edit",
            "client": client,
            "form_data": form_data,
            "errors": {}
        }
    )


@router.post("/clients/{client_id}/edit", response_class=HTMLResponse)
def update_client(
    request: Request,
    client_id: int,
    name: str = Form(""),
    email: str = Form(""),
    phone: str = Form(""),
    company: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    client = services.get_client_by_id(db, client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    form_data = {
        "name": name,
        "email": email,
        "phone": phone,
        "company": company or ""
    }
    errors = {}

    try:
        validated_data = ClientUpdate(
            name=name,
            email=email,
            phone=phone,
            company=company
        )
        services.update_client(db, client_id, validated_data)
        return RedirectResponse(
            url=f"/clients/{client_id}?msg=Cliente+actualizado+con+%C3%A9xito",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except ValidationError as ve:
        for err in ve.errors():
            field = str(err["loc"][0])
            errors[field] = err["msg"].replace("Value error, ", "")
    except services.EmailAlreadyExistsError as ee:
        errors["email"] = str(ee)

    return templates.TemplateResponse(
        request=request,
        name="clients/form.html",
        context={
            "action": "edit",
            "client": client,
            "form_data": form_data,
            "errors": errors
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@router.post("/clients/{client_id}/delete")
def delete_client(
    client_id: int,
    db: Session = Depends(get_db)
):
    try:
        services.delete_client(db, client_id)
        return RedirectResponse(
            url="/clients?msg=Cliente+eliminado+exitosamente",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except services.ClientNotFoundError:
        return RedirectResponse(
            url="/clients?error=El+cliente+no+existe",
            status_code=status.HTTP_303_SEE_OTHER
        )
