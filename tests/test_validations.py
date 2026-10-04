import pytest
from pydantic import ValidationError
from app.schemas import ClientCreate, NoteCreate


class TestClientValidationQA:
    """Suite de pruebas unitarias orientadas a QA para validar partición de equivalencia y valores límite."""

    def test_valid_client_creation(self):
        client = ClientCreate(
            name="César Augusto",
            email="cesar@example.com",
            phone="5512345678",
            company="QA Labs"
        )
        assert client.name == "César Augusto"
        assert client.email == "cesar@example.com"
        assert client.phone == "5512345678"
        assert client.company == "QA Labs"

    def test_company_field_cleaning_and_none_handling(self):
        c1 = ClientCreate(name="Tester", email="test@test.com", phone="1234567890", company=None)
        assert c1.company is None
        c2 = ClientCreate(name="Tester", email="test@test.com", phone="1234567890", company="   ")
        assert c2.company is None
        c3 = ClientCreate(name="Tester", email="test@test.com", phone="1234567890", company="  Acme Corp  ")
        assert c3.company == "Acme Corp"

    # --- NOMBRE ---
    @pytest.mark.parametrize("invalid_name", ["", "   ", "\t\n"])
    def test_name_cannot_be_empty_or_whitespace(self, invalid_name):
        with pytest.raises(ValidationError) as exc_info:
            ClientCreate(
                name=invalid_name,
                email="test@example.com",
                phone="5512345678"
            )
        assert "El nombre no puede estar vacío" in str(exc_info.value) or "at least 1 character" in str(exc_info.value)

    # --- CORREO ELECTRÓNICO ---
    @pytest.mark.parametrize("valid_email", [
        "usuario@dominio.com",
        "nombre.apellido@sub.dominio.org",
        "qa+tag@empresa.io"
    ])
    def test_valid_email_formats(self, valid_email):
        client = ClientCreate(name="Tester", email=valid_email, phone="1234567890")
        assert client.email == valid_email

    @pytest.mark.parametrize("invalid_email", [
        "correo_sin_arroba.com",
        "@dominio.com",
        "usuario@",
        "usuario@dominio",
        "espacios en@correo.com"
    ])
    def test_invalid_email_formats(self, invalid_email):
        with pytest.raises(ValidationError):
            ClientCreate(name="Tester", email=invalid_email, phone="1234567890")

    # --- TELÉFONO (10 DÍGITOS) ---
    def test_phone_exact_10_digits_valid(self):
        client = ClientCreate(name="Tester", email="test@test.com", phone="1234567890")
        assert client.phone == "1234567890"

    @pytest.mark.parametrize("invalid_phone", [
        "123456789",          # 9 dígitos (Límite inferior)
        "12345678901",        # 11 dígitos (Límite superior)
        "12345abc90",         # Caracteres alfabéticos
        "123-456-7890",       # Con guiones
        "(55)12345678",       # Con paréntesis
        "          ",         # Espacios en blanco
        "12345 67890",        # Espacio intermedio
        "!@#$%^&*()"          # Caracteres especiales
    ])
    def test_phone_boundary_and_type_failures(self, invalid_phone):
        with pytest.raises(ValidationError) as exc_info:
            ClientCreate(name="Tester", email="test@test.com", phone=invalid_phone)
        assert "El teléfono debe contener exactamente 10 dígitos numéricos." in str(exc_info.value)


class TestNoteValidationQA:
    def test_valid_note(self):
        note = NoteCreate(content="Llamada de seguimiento agendada para el lunes.")
        assert note.content == "Llamada de seguimiento agendada para el lunes."

    @pytest.mark.parametrize("empty_content", ["", "   ", "\n\t"])
    def test_empty_note_fails(self, empty_content):
        with pytest.raises(ValidationError) as exc_info:
            NoteCreate(content=empty_content)
        assert "El contenido de la nota no puede estar vacío." in str(exc_info.value) or "at least 1 character" in str(exc_info.value)
