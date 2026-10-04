from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Client, Note
from app.schemas import ClientCreate, ClientUpdate, NoteCreate


class EmailAlreadyExistsError(Exception):
    """Excepción lanzada cuando se intenta registrar un correo ya existente."""
    pass


class ClientNotFoundError(Exception):
    """Excepción lanzada cuando no se encuentra el cliente."""
    pass


class NoteNotFoundError(Exception):
    """Excepción lanzada cuando no se encuentra la nota."""
    pass


def get_clients(db: Session, search: Optional[str] = None) -> List[Client]:
    query = db.query(Client)
    if search:
        cleaned_search = search.strip()
        if cleaned_search:
            # Case-insensitive search on name
            query = query.filter(Client.name.ilike(f"%{cleaned_search}%"))
    return query.order_by(Client.name.asc()).all()


def get_client_by_id(db: Session, client_id: int) -> Optional[Client]:
    return db.query(Client).filter(Client.id == client_id).first()


def get_client_by_email(db: Session, email: str) -> Optional[Client]:
    return db.query(Client).filter(func.lower(Client.email) == email.lower().strip()).first()


def create_client(db: Session, client_data: ClientCreate) -> Client:
    existing = get_client_by_email(db, client_data.email)
    if existing:
        raise EmailAlreadyExistsError(f"El correo electrónico '{client_data.email}' ya está registrado.")

    new_client = Client(
        name=client_data.name,
        email=client_data.email.lower().strip(),
        phone=client_data.phone,
        company=client_data.company
    )
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client


def update_client(db: Session, client_id: int, client_data: ClientUpdate) -> Client:
    client = get_client_by_id(db, client_id)
    if not client:
        raise ClientNotFoundError(f"Cliente con ID {client_id} no encontrado.")

    # Check if email belongs to someone else
    existing_with_email = get_client_by_email(db, client_data.email)
    if existing_with_email and existing_with_email.id != client_id:
        raise EmailAlreadyExistsError(f"El correo electrónico '{client_data.email}' ya pertenece a otro cliente.")

    client.name = client_data.name
    client.email = client_data.email.lower().strip()
    client.phone = client_data.phone
    client.company = client_data.company

    db.commit()
    db.refresh(client)
    return client


def delete_client(db: Session, client_id: int) -> bool:
    client = get_client_by_id(db, client_id)
    if not client:
        raise ClientNotFoundError(f"Cliente con ID {client_id} no encontrado.")

    db.delete(client)
    db.commit()
    return True


def create_note(db: Session, client_id: int, note_data: NoteCreate) -> Note:
    client = get_client_by_id(db, client_id)
    if not client:
        raise ClientNotFoundError(f"Cliente con ID {client_id} no encontrado.")

    note = Note(
        client_id=client_id,
        content=note_data.content
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def delete_note(db: Session, note_id: int) -> bool:
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise NoteNotFoundError(f"Nota con ID {note_id} no encontrada.")

    db.delete(note)
    db.commit()
    return True
