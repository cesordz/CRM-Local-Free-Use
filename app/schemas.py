import re
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


class NoteBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="Contenido de la nota")

    @field_validator("content")
    @classmethod
    def validate_content_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("El contenido de la nota no puede estar vacío.")
        return stripped


class NoteCreate(NoteBase):
    pass


class NoteResponse(NoteBase):
    id: int
    client_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Nombre completo del cliente")
    email: EmailStr = Field(..., description="Correo electrónico único del cliente")
    phone: str = Field(..., description="Teléfono de 10 dígitos numéricos")
    company: Optional[str] = Field(None, max_length=100, description="Empresa u organización")

    @field_validator("name")
    @classmethod
    def validate_name_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("El nombre no puede estar vacío ni contener solo espacios.")
        return stripped

    @field_validator("phone")
    @classmethod
    def validate_phone_ten_digits(cls, v: str) -> str:
        stripped = v.strip()
        if not re.fullmatch(r"^\d{10}$", stripped):
            raise ValueError("El teléfono debe contener exactamente 10 dígitos numéricos.")
        return stripped

    @field_validator("company")
    @classmethod
    def clean_company(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            return stripped if stripped else None
        return None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(ClientBase):
    pass


class ClientResponse(ClientBase):
    id: int
    created_at: datetime
    notes: List[NoteResponse] = []

    model_config = ConfigDict(from_attributes=True)
