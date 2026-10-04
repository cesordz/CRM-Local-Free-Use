from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ClientCreate, ClientUpdate, ClientResponse, NoteCreate, NoteResponse
from app import services

api_router = APIRouter(prefix="/api", tags=["API REST"])


@api_router.get("/clients", response_model=List[ClientResponse])
def get_clients_api(q: Optional[str] = None, db: Session = Depends(get_db)):
    return services.get_clients(db, search=q)


@api_router.post("/clients", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client_api(client_in: ClientCreate, db: Session = Depends(get_db)):
    try:
        return services.create_client(db, client_in)
    except services.EmailAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@api_router.get("/clients/{client_id}", response_model=ClientResponse)
def get_client_api(client_id: int, db: Session = Depends(get_db)):
    client = services.get_client_by_id(db, client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    return client


@api_router.put("/clients/{client_id}", response_model=ClientResponse)
def update_client_api(client_id: int, client_in: ClientUpdate, db: Session = Depends(get_db)):
    try:
        return services.update_client(db, client_id, client_in)
    except services.ClientNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except services.EmailAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@api_router.delete("/clients/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client_api(client_id: int, db: Session = Depends(get_db)):
    try:
        services.delete_client(db, client_id)
        return None
    except services.ClientNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@api_router.post("/clients/{client_id}/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def add_note_api(client_id: int, note_in: NoteCreate, db: Session = Depends(get_db)):
    try:
        return services.create_note(db, client_id, note_in)
    except services.ClientNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@api_router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note_api(note_id: int, db: Session = Depends(get_db)):
    try:
        services.delete_note(db, note_id)
        return None
    except services.NoteNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
