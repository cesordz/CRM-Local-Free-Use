import pytest
from app import services
from app.models import Client, Note
from app.schemas import ClientCreate, ClientUpdate, NoteCreate


class TestClientServiceHappyPath:
    """Pruebas del caso feliz para las operaciones de la capa de servicios."""

    def test_create_client_successfully_persists_in_database(self, db_session, sample_client_payload):
        client_in = ClientCreate(**sample_client_payload)
        client = services.create_client(db_session, client_in)

        assert client.id is not None
        assert client.name == sample_client_payload["name"]
        assert client.email == sample_client_payload["email"].lower()
        assert client.phone == sample_client_payload["phone"]
        assert client.company == sample_client_payload["company"]
        assert client.created_at is not None

        # Verificar persistencia en base de datos
        persisted = db_session.query(Client).filter(Client.id == client.id).first()
        assert persisted is not None
        assert persisted.email == sample_client_payload["email"].lower()

    def test_get_client_by_id_returns_correct_client(self, db_session, sample_client_payload):
        client_in = ClientCreate(**sample_client_payload)
        created = services.create_client(db_session, client_in)

        retrieved = services.get_client_by_id(db_session, created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == sample_client_payload["name"]

    def test_get_client_by_email_case_insensitive_and_trimmed(self, db_session, sample_client_payload):
        client_in = ClientCreate(**sample_client_payload)
        created = services.create_client(db_session, client_in)

        # Búsqueda con mayúsculas y espacios alrededor
        query_email = f"  {sample_client_payload['email'].upper()}  "
        retrieved = services.get_client_by_email(db_session, query_email)

        assert retrieved is not None
        assert retrieved.id == created.id

    def test_get_clients_returns_all_ordered_by_name_asc(self, db_session):
        client_b = ClientCreate(name="Beto Pérez", email="beto@test.com", phone="1111111111")
        client_a = ClientCreate(name="Ana López", email="ana@test.com", phone="2222222222")
        client_c = ClientCreate(name="Carlos Ortiz", email="carlos@test.com", phone="3333333333")

        services.create_client(db_session, client_b)
        services.create_client(db_session, client_a)
        services.create_client(db_session, client_c)

        clients = services.get_clients(db_session)
        assert len(clients) == 3
        assert [c.name for c in clients] == ["Ana López", "Beto Pérez", "Carlos Ortiz"]

    def test_get_clients_with_search_filter_matches_name_substring(self, db_session):
        client1 = ClientCreate(name="Fernando Valenzuela", email="fernando@test.com", phone="1111111111")
        client2 = ClientCreate(name="María Fernanda", email="maria@test.com", phone="2222222222")
        client3 = ClientCreate(name="Roberto Gomez", email="roberto@test.com", phone="3333333333")

        services.create_client(db_session, client1)
        services.create_client(db_session, client2)
        services.create_client(db_session, client3)

        results = services.get_clients(db_session, search="fernand")
        assert len(results) == 2
        names = [c.name for c in results]
        assert "Fernando Valenzuela" in names
        assert "María Fernanda" in names
        assert "Roberto Gomez" not in names

    def test_get_clients_with_whitespace_only_search_returns_all(self, db_session, sample_client_payload):
        services.create_client(db_session, ClientCreate(**sample_client_payload))
        results = services.get_clients(db_session, search="   ")
        assert len(results) == 1

    def test_update_client_modifies_data_successfully(self, db_session, sample_client_payload):
        created = services.create_client(db_session, ClientCreate(**sample_client_payload))

        update_data = ClientUpdate(
            name="Lucía Morales Actualizada",
            email="lucia.nueva@empresa.com",
            phone="5587654321",
            company="Nueva Empresa S.A."
        )
        updated = services.update_client(db_session, created.id, update_data)

        assert updated.id == created.id
        assert updated.name == "Lucía Morales Actualizada"
        assert updated.email == "lucia.nueva@empresa.com"
        assert updated.phone == "5587654321"
        assert updated.company == "Nueva Empresa S.A."

    def test_update_client_keeping_same_email_is_allowed(self, db_session, sample_client_payload):
        created = services.create_client(db_session, ClientCreate(**sample_client_payload))

        # Actualizar datos conservando el mismo email
        update_data = ClientUpdate(
            name="Lucía Morales Misma",
            email=sample_client_payload["email"],
            phone="5512345678",
            company=sample_client_payload["company"]
        )
        updated = services.update_client(db_session, created.id, update_data)
        assert updated.name == "Lucía Morales Misma"
        assert updated.email == sample_client_payload["email"].lower()

    def test_create_note_associates_correctly_with_client(self, db_session, sample_client_payload):
        client = services.create_client(db_session, ClientCreate(**sample_client_payload))
        note_in = NoteCreate(content="Cliente interesado en plan corporativo.")

        note = services.create_note(db_session, client.id, note_in)
        assert note.id is not None
        assert note.client_id == client.id
        assert note.content == "Cliente interesado en plan corporativo."
        assert note.created_at is not None

        # Verificar en base de datos
        db_note = db_session.query(Note).filter(Note.id == note.id).first()
        assert db_note is not None
        assert db_note.client_id == client.id


class TestClientServiceDuplicateEmail:
    """Pruebas de validación de email duplicado en capa de servicios."""

    def test_create_client_raises_exception_on_duplicate_email(self, db_session, sample_client_payload):
        services.create_client(db_session, ClientCreate(**sample_client_payload))

        # Intentar crear un segundo cliente con el mismo email (incluso con mayúsculas/espacios)
        duplicate_in = ClientCreate(
            name="Otro Nombre",
            email=sample_client_payload["email"].upper(),
            phone="5599887766",
            company="Otra Empresa"
        )

        with pytest.raises(services.EmailAlreadyExistsError) as exc_info:
            services.create_client(db_session, duplicate_in)

        assert "ya está registrado" in str(exc_info.value)

    def test_update_client_raises_exception_when_email_belongs_to_another_client(self, db_session):
        client1 = services.create_client(
            db_session,
            ClientCreate(name="Cliente Uno", email="uno@empresa.com", phone="1111111111")
        )
        client2 = services.create_client(
            db_session,
            ClientCreate(name="Cliente Dos", email="dos@empresa.com", phone="2222222222")
        )

        # Intentar que client2 use el email de client1
        update_data = ClientUpdate(
            name="Cliente Dos Renombrado",
            email="uno@empresa.com",
            phone="2222222222"
        )

        with pytest.raises(services.EmailAlreadyExistsError) as exc_info:
            services.update_client(db_session, client2.id, update_data)

        assert "ya pertenece a otro cliente" in str(exc_info.value)


class TestClientServiceNonExistentEntities:
    """Pruebas para manejo de clientes o notas inexistentes en la capa de servicios."""

    def test_get_client_by_id_returns_none_for_nonexistent_id(self, db_session):
        client = services.get_client_by_id(db_session, 99999)
        assert client is None

    def test_get_client_by_email_returns_none_for_nonexistent_email(self, db_session):
        client = services.get_client_by_email(db_session, "noexiste@correo.com")
        assert client is None

    def test_update_client_raises_exception_when_client_does_not_exist(self, db_session):
        update_data = ClientUpdate(
            name="Fantasma",
            email="fantasma@empresa.com",
            phone="5500000000"
        )
        with pytest.raises(services.ClientNotFoundError) as exc_info:
            services.update_client(db_session, 99999, update_data)

        assert "Cliente con ID 99999 no encontrado" in str(exc_info.value)

    def test_delete_client_raises_exception_when_client_does_not_exist(self, db_session):
        with pytest.raises(services.ClientNotFoundError) as exc_info:
            services.delete_client(db_session, 99999)

        assert "Cliente con ID 99999 no encontrado" in str(exc_info.value)

    def test_create_note_raises_exception_when_client_does_not_exist(self, db_session):
        note_in = NoteCreate(content="Nota para cliente inexistente")
        with pytest.raises(services.ClientNotFoundError) as exc_info:
            services.create_note(db_session, 99999, note_in)

        assert "Cliente con ID 99999 no encontrado" in str(exc_info.value)

    def test_delete_note_raises_exception_when_note_does_not_exist(self, db_session):
        with pytest.raises(services.NoteNotFoundError) as exc_info:
            services.delete_note(db_session, 88888)

        assert "Nota con ID 88888 no encontrada" in str(exc_info.value)


class TestClientServiceDeletion:
    """Pruebas de eliminación exitosa y efectos en la capa de servicios."""

    def test_delete_client_success_removes_record(self, db_session, sample_client_payload):
        client = services.create_client(db_session, ClientCreate(**sample_client_payload))
        client_id = client.id

        result = services.delete_client(db_session, client_id)
        assert result is True

        # Verificar que ya no existe en la base de datos
        assert services.get_client_by_id(db_session, client_id) is None
        assert db_session.query(Client).filter(Client.id == client_id).first() is None

    def test_delete_note_success_removes_note_record(self, db_session, sample_client_payload):
        client = services.create_client(db_session, ClientCreate(**sample_client_payload))
        note = services.create_note(db_session, client.id, NoteCreate(content="Nota de prueba"))
        note_id = note.id

        result = services.delete_note(db_session, note_id)
        assert result is True

        # Verificar que la nota ya no existe
        assert db_session.query(Note).filter(Note.id == note_id).first() is None

    def test_delete_client_cascades_and_removes_associated_notes(self, db_session, sample_client_payload):
        client = services.create_client(db_session, ClientCreate(**sample_client_payload))
        services.create_note(db_session, client.id, NoteCreate(content="Nota 1"))
        services.create_note(db_session, client.id, NoteCreate(content="Nota 2"))

        # Confirmar que existen 2 notas antes de eliminar el cliente
        assert db_session.query(Note).filter(Note.client_id == client.id).count() == 2

        # Eliminar cliente
        services.delete_client(db_session, client.id)

        # Confirmar eliminación en cascada
        assert db_session.query(Note).filter(Note.client_id == client.id).count() == 0


def test_database_get_db_session_lifecycle():
    """Prueba unitaria para verificar que la dependencia get_db genera y cierra la sesión."""
    from app.database import get_db
    gen = get_db()
    session = next(gen)
    assert session is not None
    try:
        pass
    finally:
        try:
            next(gen)
        except StopIteration:
            pass
