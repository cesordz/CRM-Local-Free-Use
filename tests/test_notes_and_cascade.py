from app.models import Client, Note


def test_add_and_delete_note_via_form(client):
    # 1. Crear cliente
    client.post("/clients/new", data={
        "name": "Cliente con Notas",
        "email": "notas@empresa.com",
        "phone": "5544332211"
    })
    # Obtener el ID del cliente creado
    list_res = client.get("/clients")
    assert "Cliente con Notas" in list_res.text

    # Recuperar ID mediante el listado API
    api_list = client.get("/api/clients").json()
    created = [c for c in api_list if c["email"] == "notas@empresa.com"][0]
    client_id = created["id"]

    # 2. Agregar nota válida mediante formulario
    add_note_res = client.post(
        f"/clients/{client_id}/notes",
        data={"content": "Primera llamada de prospección exitosa."},
        follow_redirects=True
    )
    assert add_note_res.status_code == 200
    assert "Primera llamada de prospección exitosa." in add_note_res.text
    assert "Nota agregada exitosamente" in add_note_res.text

    # 3. Intentar agregar nota vacía (validación esperada 422)
    empty_note_res = client.post(
        f"/clients/{client_id}/notes",
        data={"content": "    "}
    )
    assert empty_note_res.status_code == 422
    assert 'data-testid="error-note-content"' in empty_note_res.text


def test_cascade_delete_notes_when_client_deleted(client, db_session):
    """Prueba de integridad referencial: Al eliminar un cliente, sus notas deben eliminarse en cascada."""
    # 1. Crear cliente via API
    create_res = client.post("/api/clients", json={
        "name": "Cliente Cascada",
        "email": "cascada@test.com",
        "phone": "5511223344"
    })
    client_id = create_res.json()["id"]

    # 2. Agregar dos notas
    client.post(f"/api/clients/{client_id}/notes", json={"content": "Nota 1 para borrar"})
    client.post(f"/api/clients/{client_id}/notes", json={"content": "Nota 2 para borrar"})

    # Verificar en la sesión de base de datos que existan 2 notas
    notes_before = db_session.query(Note).filter(Note.client_id == client_id).all()
    assert len(notes_before) == 2

    # 3. Eliminar el cliente
    del_res = client.post(f"/clients/{client_id}/delete", follow_redirects=True)
    assert del_res.status_code == 200

    # 4. Verificar que en la base de datos ya no existan las notas asociadas
    notes_after = db_session.query(Note).filter(Note.client_id == client_id).all()
    assert len(notes_after) == 0

    # Verificar que el cliente tampoco exista
    client_in_db = db_session.query(Client).filter(Client.id == client_id).first()
    assert client_in_db is None
