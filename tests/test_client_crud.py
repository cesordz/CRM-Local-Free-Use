def test_list_clients_empty(client):
    response = client.get("/clients")
    assert response.status_code == 200
    assert "Aún no hay clientes registrados" in response.text
    assert 'data-testid="empty-clients-state"' in response.text


def test_create_client_form_success(client):
    form_data = {
        "name": "Valeria Gómez",
        "email": "valeria@tech.com",
        "phone": "5598765432",
        "company": "Tech Innovations"
    }
    response = client.post("/clients/new", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert "Valeria Gómez" in response.text
    assert "5598765432" in response.text
    assert "Tech Innovations" in response.text
    assert "Cliente creado con éxito" in response.text


def test_create_client_validation_error_phone_length(client):
    # Teléfono inválido de 8 dígitos
    form_data = {
        "name": "Carlos Ruiz",
        "email": "carlos@test.com",
        "phone": "12345678",
        "company": "QA Test"
    }
    response = client.post("/clients/new", data=form_data)
    assert response.status_code == 422
    assert "El teléfono debe contener exactamente 10 dígitos numéricos." in response.text
    assert 'data-testid="error-phone"' in response.text
    # Asegurar que los datos ingresados se preserven en el formulario
    assert 'value="Carlos Ruiz"' in response.text


def test_create_client_validation_error_duplicate_email(client):
    client_data = {
        "name": "Original User",
        "email": "repetido@empresa.com",
        "phone": "1111111111",
        "company": "Original Corp"
    }
    res1 = client.post("/clients/new", data=client_data, follow_redirects=True)
    assert res1.status_code == 200

    # Intento de duplicar el correo
    res2 = client.post("/clients/new", data={
        "name": "Duplicate User",
        "email": "repetido@empresa.com",
        "phone": "2222222222"
    })
    assert res2.status_code == 422
    assert "ya está registrado" in res2.text
    assert 'data-testid="error-email"' in res2.text


def test_search_clients_by_name(client):
    client.post("/clients/new", data={"name": "Alfonso Cuarón", "email": "alfonso@cinema.com", "phone": "1234567890"})
    client.post("/clients/new", data={"name": "Guillermo del Toro", "email": "memo@cinema.com", "phone": "0987654321"})

    # Búsqueda coincidente
    res_search = client.get("/clients?q=Guillermo")
    assert res_search.status_code == 200
    assert "Guillermo del Toro" in res_search.text
    assert "Alfonso Cuarón" not in res_search.text

    # Búsqueda no coincidente
    res_none = client.get("/clients?q=Inexistente")
    assert res_none.status_code == 200
    assert "No se encontraron resultados" in res_none.text


def test_api_rest_full_crud_lifecycle(client):
    # 1. Crear via API
    payload = {
        "name": "Elena Torres",
        "email": "elena@api.com",
        "phone": "5500001122",
        "company": "API Tester"
    }
    create_res = client.post("/api/clients", json=payload)
    assert create_res.status_code == 201
    data = create_res.json()
    client_id = data["id"]
    assert data["name"] == "Elena Torres"
    assert data["phone"] == "5500001122"

    # 2. Conflicto por email duplicado en API
    dup_res = client.post("/api/clients", json=payload)
    assert dup_res.status_code == 409
    assert "ya está registrado" in dup_res.json()["detail"]

    # 3. Leer detalle via API
    get_res = client.get(f"/api/clients/{client_id}")
    assert get_res.status_code == 200
    assert get_res.json()["email"] == "elena@api.com"

    # 4. Actualizar via API
    update_payload = {
        "name": "Elena Torres Modificada",
        "email": "elena@api.com",
        "phone": "5599998877",
        "company": "New Corp"
    }
    put_res = client.put(f"/api/clients/{client_id}", json=update_payload)
    assert put_res.status_code == 200
    assert put_res.json()["name"] == "Elena Torres Modificada"
    assert put_res.json()["phone"] == "5599998877"

    # 5. Eliminar via API
    del_res = client.delete(f"/api/clients/{client_id}")
    assert del_res.status_code == 204

    # 6. Verificar 404 post-eliminación
    verify_res = client.get(f"/api/clients/{client_id}")
    assert verify_res.status_code == 404


def test_edit_client_via_web_form(client):
    # Crear cliente inicial
    init_res = client.post("/clients/new", data={
        "name": "Cliente Inicial",
        "email": "inicial@empresa.com",
        "phone": "5511223344",
        "company": "Empresa A"
    }, follow_redirects=True)
    assert init_res.status_code == 200

    # Obtener ID
    api_list = client.get("/api/clients").json()
    client_id = [c for c in api_list if c["email"] == "inicial@empresa.com"][0]["id"]

    # Acceder a la pantalla de edición
    edit_page = client.get(f"/clients/{client_id}/edit")
    assert edit_page.status_code == 200
    assert 'value="Cliente Inicial"' in edit_page.text

    # Guardar cambios válidos
    update_res = client.post(f"/clients/{client_id}/edit", data={
        "name": "Cliente Actualizado",
        "email": "actualizado@empresa.com",
        "phone": "5599887766",
        "company": "Empresa B"
    }, follow_redirects=True)
    assert update_res.status_code == 200
    assert "Cliente Actualizado" in update_res.text
    assert "actualizado@empresa.com" in update_res.text
    assert "Cliente actualizado con éxito" in update_res.text

    # Intentar actualización con teléfono inválido (debe fallar 422)
    invalid_res = client.post(f"/clients/{client_id}/edit", data={
        "name": "Cliente Actualizado",
        "email": "actualizado@empresa.com",
        "phone": "999",
        "company": "Empresa B"
    })
    assert invalid_res.status_code == 422
    assert "El teléfono debe contener exactamente 10 dígitos numéricos." in invalid_res.text
    assert 'data-testid="error-phone"' in invalid_res.text


def test_delete_client_via_web_form(client):
    # Crear cliente para borrar
    client.post("/clients/new", data={
        "name": "Para Borrar",
        "email": "borrar@empresa.com",
        "phone": "5500000000"
    }, follow_redirects=True)

    api_list = client.get("/api/clients").json()
    client_id = [c for c in api_list if c["email"] == "borrar@empresa.com"][0]["id"]

    # Borrar via formulario
    delete_res = client.post(f"/clients/{client_id}/delete", follow_redirects=True)
    assert delete_res.status_code == 200
    assert "Cliente eliminado exitosamente" in delete_res.text
    assert "Para Borrar" not in delete_res.text
