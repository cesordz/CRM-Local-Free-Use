import pytest
from unittest.mock import patch


class TestEndpointsHappyPath:
    """Pruebas de endpoints para el caso feliz (API REST y Vistas Web) usando TestClient."""

    def test_endpoint_api_create_client_happy_path(self, client, sample_client_payload):
        response = client.post("/api/clients", json=sample_client_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["name"] == sample_client_payload["name"]
        assert data["email"] == sample_client_payload["email"].lower()
        assert data["phone"] == sample_client_payload["phone"]
        assert data["company"] == sample_client_payload["company"]

    def test_endpoint_api_get_client_by_id_happy_path(self, client, sample_client_payload):
        create_res = client.post("/api/clients", json=sample_client_payload)
        client_id = create_res.json()["id"]

        get_res = client.get(f"/api/clients/{client_id}")
        assert get_res.status_code == 200
        assert get_res.json()["id"] == client_id
        assert get_res.json()["name"] == sample_client_payload["name"]

    def test_endpoint_api_list_clients_happy_path(self, client, sample_client_payload):
        client.post("/api/clients", json=sample_client_payload)
        list_res = client.get("/api/clients")
        assert list_res.status_code == 200
        data = list_res.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_endpoint_api_search_clients_happy_path(self, client):
        client.post("/api/clients", json={"name": "Diana Prince", "email": "diana@amazon.com", "phone": "5511223344"})
        client.post("/api/clients", json={"name": "Clark Kent", "email": "clark@planet.com", "phone": "5599887766"})

        search_res = client.get("/api/clients?q=Diana")
        assert search_res.status_code == 200
        results = search_res.json()
        assert len(results) == 1
        assert results[0]["name"] == "Diana Prince"

    def test_endpoint_api_update_client_happy_path(self, client, sample_client_payload):
        create_res = client.post("/api/clients", json=sample_client_payload)
        client_id = create_res.json()["id"]

        update_payload = {
            "name": "Lucía Morales Modificada",
            "email": "lucia.nueva@empresa.com",
            "phone": "5500000000",
            "company": "Empresa Modificada"
        }
        put_res = client.put(f"/api/clients/{client_id}", json=update_payload)
        assert put_res.status_code == 200
        data = put_res.json()
        assert data["name"] == "Lucía Morales Modificada"
        assert data["email"] == "lucia.nueva@empresa.com"
        assert data["phone"] == "5500000000"

    def test_endpoint_api_create_note_happy_path(self, client, sample_client_payload):
        create_client_res = client.post("/api/clients", json=sample_client_payload)
        client_id = create_client_res.json()["id"]

        note_payload = {"content": "Llamada inicial realizada con éxito."}
        note_res = client.post(f"/api/clients/{client_id}/notes", json=note_payload)
        assert note_res.status_code == 201
        data = note_res.json()
        assert data["id"] is not None
        assert data["client_id"] == client_id
        assert data["content"] == "Llamada inicial realizada con éxito."

    def test_endpoint_web_root_redirects_to_clients(self, client):
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["location"] == "/clients"

    def test_endpoint_web_list_clients_page_returns_200(self, client):
        response = client.get("/clients")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_endpoint_web_new_client_page_returns_200(self, client):
        response = client.get("/clients/new")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_endpoint_web_create_client_happy_path(self, client, sample_client_payload):
        response = client.post("/clients/new", data=sample_client_payload, follow_redirects=False)
        assert response.status_code == 303
        assert "/clients/" in response.headers["location"]

    def test_endpoint_web_client_detail_page_happy_path(self, client, sample_client_payload):
        create_res = client.post("/api/clients", json=sample_client_payload)
        client_id = create_res.json()["id"]

        detail_res = client.get(f"/clients/{client_id}")
        assert detail_res.status_code == 200
        assert sample_client_payload["name"] in detail_res.text

    def test_endpoint_web_edit_client_page_happy_path(self, client, sample_client_payload):
        create_res = client.post("/api/clients", json=sample_client_payload)
        client_id = create_res.json()["id"]

        edit_res = client.get(f"/clients/{client_id}/edit")
        assert edit_res.status_code == 200
        assert f'value="{sample_client_payload["name"]}"' in edit_res.text

    def test_endpoint_web_update_client_happy_path(self, client, sample_client_payload):
        create_res = client.post("/api/clients", json=sample_client_payload)
        client_id = create_res.json()["id"]

        update_form = {
            "name": "Nombre Actualizado",
            "email": "actualizado@empresa.com",
            "phone": "5533334444",
            "company": "Compañía Renovada"
        }
        post_edit_res = client.post(f"/clients/{client_id}/edit", data=update_form, follow_redirects=False)
        assert post_edit_res.status_code == 303
        response_redirects_to = post_edit_res.headers["location"]
        assert f"/clients/{client_id}" in response_redirects_to

    def test_endpoint_web_add_note_happy_path(self, client, sample_client_payload):
        create_res = client.post("/api/clients", json=sample_client_payload)
        client_id = create_res.json()["id"]

        note_form = {"content": "Nota de seguimiento enviada por formulario"}
        post_note_res = client.post(f"/clients/{client_id}/notes", data=note_form, follow_redirects=False)
        assert post_note_res.status_code == 303
        assert f"/clients/{client_id}" in post_note_res.headers["location"]


class TestEndpointsDuplicateEmail:
    """Pruebas de endpoints para detección y rechazo de correos electrónicos duplicados."""

    def test_endpoint_api_create_client_duplicate_email_returns_409(self, client, sample_client_payload):
        client.post("/api/clients", json=sample_client_payload)

        # Intento de duplicación
        res_dup = client.post("/api/clients", json=sample_client_payload)
        assert res_dup.status_code == 409
        detail = res_dup.json()["detail"]
        assert "ya está registrado" in detail

    def test_endpoint_api_update_client_duplicate_email_returns_409(self, client):
        res1 = client.post("/api/clients", json={"name": "Cliente A", "email": "a@empresa.com", "phone": "1111111111"})
        res2 = client.post("/api/clients", json={"name": "Cliente B", "email": "b@empresa.com", "phone": "2222222222"})
        client_b_id = res2.json()["id"]

        # Intentar actualizar B para que use el email de A
        put_res = client.put(f"/api/clients/{client_b_id}", json={
            "name": "Cliente B Actualizado",
            "email": "a@empresa.com",
            "phone": "2222222222"
        })
        assert put_res.status_code == 409
        assert "ya pertenece a otro cliente" in put_res.json()["detail"]

    def test_endpoint_web_create_client_duplicate_email_returns_422(self, client, sample_client_payload):
        client.post("/clients/new", data=sample_client_payload)

        # Intento de duplicar por formulario web
        res_dup = client.post("/clients/new", data=sample_client_payload)
        assert res_dup.status_code == 422
        assert "ya está registrado" in res_dup.text

    def test_endpoint_web_update_client_duplicate_email_returns_422(self, client):
        res1 = client.post("/api/clients", json={"name": "Cliente 1", "email": "c1@test.com", "phone": "1111111111"})
        res2 = client.post("/api/clients", json={"name": "Cliente 2", "email": "c2@test.com", "phone": "2222222222"})
        client_2_id = res2.json()["id"]

        # Actualizar via web usando el email de cliente 1
        res = client.post(f"/clients/{client_2_id}/edit", data={
            "name": "Cliente 2",
            "email": "c1@test.com",
            "phone": "2222222222"
        })
        assert res.status_code == 422
        assert "ya pertenece a otro cliente" in res.text


class TestEndpointsInvalidEmail:
    """Pruebas de endpoints para validación de formato de correo electrónico inválido."""

    @pytest.mark.parametrize("bad_email", [
        "correo-sin-arroba.com",
        "usuario@",
        "@dominio.com",
        "usuario@dominio",
        "espacios en@correo.com"
    ])
    def test_endpoint_api_create_client_invalid_email_returns_422(self, client, bad_email):
        payload = {
            "name": "Prueba Formato",
            "email": bad_email,
            "phone": "5512345678"
        }
        response = client.post("/api/clients", json=payload)
        assert response.status_code == 422

    def test_endpoint_api_update_client_invalid_email_returns_422(self, client, sample_client_payload):
        create_res = client.post("/api/clients", json=sample_client_payload)
        client_id = create_res.json()["id"]

        update_payload = {
            "name": "Nombre Válido",
            "email": "email_invalido_sin_formato",
            "phone": "5512345678"
        }
        put_res = client.put(f"/api/clients/{client_id}", json=update_payload)
        assert put_res.status_code == 422

    def test_endpoint_web_create_client_invalid_email_returns_422(self, client):
        form_data = {
            "name": "Cliente Web",
            "email": "invalido-sin-arroba",
            "phone": "5512345678"
        }
        response = client.post("/clients/new", data=form_data)
        assert response.status_code == 422
        assert "value is not a valid email address" in response.text or "correo" in response.text

    def test_endpoint_web_update_client_invalid_email_returns_422(self, client, sample_client_payload):
        create_res = client.post("/api/clients", json=sample_client_payload)
        client_id = create_res.json()["id"]

        form_data = {
            "name": "Cliente Modificado",
            "email": "email_totalmente_invalido",
            "phone": "5512345678"
        }
        response = client.post(f"/clients/{client_id}/edit", data=form_data)
        assert response.status_code == 422


class TestEndpointsEmptyFields:
    """Pruebas de endpoints para rechazo de campos obligatorios vacíos o con solo espacios."""

    @pytest.mark.parametrize("empty_name", ["", "   ", "\t\n"])
    def test_endpoint_api_create_client_empty_name_returns_422(self, client, empty_name):
        payload = {
            "name": empty_name,
            "email": "valido@test.com",
            "phone": "5512345678"
        }
        res = client.post("/api/clients", json=payload)
        assert res.status_code == 422

    def test_endpoint_api_create_client_missing_body_returns_422(self, client):
        res = client.post("/api/clients", json={})
        assert res.status_code == 422

    @pytest.mark.parametrize("empty_content", ["", "   ", "\t"])
    def test_endpoint_api_create_note_empty_content_returns_422(self, client, sample_client_payload, empty_content):
        create_res = client.post("/api/clients", json=sample_client_payload)
        client_id = create_res.json()["id"]

        res = client.post(f"/api/clients/{client_id}/notes", json={"content": empty_content})
        assert res.status_code == 422

    def test_endpoint_web_create_client_empty_name_returns_422(self, client):
        form_data = {
            "name": "   ",
            "email": "webempty@test.com",
            "phone": "5512345678"
        }
        res = client.post("/clients/new", data=form_data)
        assert res.status_code == 422
        assert "El nombre no puede estar vacío" in res.text

    def test_endpoint_web_update_client_empty_name_returns_422(self, client, sample_client_payload):
        create_res = client.post("/api/clients", json=sample_client_payload)
        client_id = create_res.json()["id"]

        form_data = {
            "name": "   ",
            "email": "webempty@test.com",
            "phone": "5512345678"
        }
        res = client.post(f"/clients/{client_id}/edit", data=form_data)
        assert res.status_code == 422
        assert "El nombre no puede estar vacío" in res.text

    def test_endpoint_web_add_note_empty_content_returns_422(self, client, sample_client_payload):
        create_res = client.post("/api/clients", json=sample_client_payload)
        client_id = create_res.json()["id"]

        res = client.post(f"/clients/{client_id}/notes", data={"content": "    "})
        assert res.status_code == 422
        assert "El contenido de la nota no puede estar vacío" in res.text


class TestEndpointsPhoneBoundaryValues:
    """Pruebas de valores límite para el teléfono (9 dígitos, 10 dígitos y 11 dígitos)."""

    def test_endpoint_api_phone_boundary_9_digits_fails_422(self, client):
        # Límite inferior no válido: 9 dígitos
        payload = {
            "name": "Cliente 9 Dígitos",
            "email": "nueve@test.com",
            "phone": "123456789"
        }
        res = client.post("/api/clients", json=payload)
        assert res.status_code == 422
        assert "El teléfono debe contener exactamente 10 dígitos numéricos." in res.text

    def test_endpoint_api_phone_boundary_10_digits_succeeds_201(self, client):
        # Límite exacto válido: 10 dígitos
        payload = {
            "name": "Cliente 10 Dígitos",
            "email": "diez@test.com",
            "phone": "1234567890"
        }
        res = client.post("/api/clients", json=payload)
        assert res.status_code == 201
        assert res.json()["phone"] == "1234567890"

    def test_endpoint_api_phone_boundary_11_digits_fails_422(self, client):
        # Límite superior no válido: 11 dígitos
        payload = {
            "name": "Cliente 11 Dígitos",
            "email": "once@test.com",
            "phone": "12345678901"
        }
        res = client.post("/api/clients", json=payload)
        assert res.status_code == 422
        assert "El teléfono debe contener exactamente 10 dígitos numéricos." in res.text

    def test_endpoint_web_phone_boundary_9_digits_fails_422(self, client):
        # Vistas Web: 9 dígitos
        form_data = {
            "name": "Web 9 Dígitos",
            "email": "web9@test.com",
            "phone": "123456789"
        }
        res = client.post("/clients/new", data=form_data)
        assert res.status_code == 422
        assert "El teléfono debe contener exactamente 10 dígitos numéricos." in res.text

    def test_endpoint_web_phone_boundary_10_digits_succeeds_303(self, client):
        # Vistas Web: 10 dígitos
        form_data = {
            "name": "Web 10 Dígitos",
            "email": "web10@test.com",
            "phone": "1234567890"
        }
        res = client.post("/clients/new", data=form_data, follow_redirects=False)
        assert res.status_code == 303

    def test_endpoint_web_phone_boundary_11_digits_fails_422(self, client):
        # Vistas Web: 11 dígitos
        form_data = {
            "name": "Web 11 Dígitos",
            "email": "web11@test.com",
            "phone": "12345678901"
        }
        res = client.post("/clients/new", data=form_data)
        assert res.status_code == 422
        assert "El teléfono debe contener exactamente 10 dígitos numéricos." in res.text

    def test_endpoint_api_update_phone_boundary_values(self, client, sample_client_payload):
        create_res = client.post("/api/clients", json=sample_client_payload)
        client_id = create_res.json()["id"]

        # Intento con 9 dígitos en PUT
        res_9 = client.put(f"/api/clients/{client_id}", json={
            "name": "Nombre",
            "email": "update@test.com",
            "phone": "123456789"
        })
        assert res_9.status_code == 422

        # Intento con 11 dígitos en PUT
        res_11 = client.put(f"/api/clients/{client_id}", json={
            "name": "Nombre",
            "email": "update@test.com",
            "phone": "12345678901"
        })
        assert res_11.status_code == 422

        # Intento con 10 dígitos en PUT (éxito)
        res_10 = client.put(f"/api/clients/{client_id}", json={
            "name": "Nombre",
            "email": "update@test.com",
            "phone": "9876543210"
        })
        assert res_10.status_code == 200
        assert res_10.json()["phone"] == "9876543210"


class TestEndpointsNonExistentClient:
    """Pruebas de endpoints para consultas y operaciones sobre clientes inexistentes."""

    def test_endpoint_api_get_nonexistent_client_returns_404(self, client):
        response = client.get("/api/clients/99999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Cliente no encontrado"

    def test_endpoint_api_update_nonexistent_client_returns_404(self, client):
        payload = {
            "name": "Fantasma",
            "email": "fantasma@test.com",
            "phone": "5500000000"
        }
        response = client.put("/api/clients/99999", json=payload)
        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"]

    def test_endpoint_api_delete_nonexistent_client_returns_404(self, client):
        response = client.delete("/api/clients/99999")
        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"]

    def test_endpoint_api_add_note_to_nonexistent_client_returns_404(self, client):
        response = client.post("/api/clients/99999/notes", json={"content": "Nota a cliente que no existe"})
        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"]

    def test_endpoint_web_get_nonexistent_client_returns_404(self, client):
        response = client.get("/clients/99999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Cliente no encontrado"

    def test_endpoint_web_edit_nonexistent_client_returns_404(self, client):
        response = client.get("/clients/99999/edit")
        assert response.status_code == 404
        assert response.json()["detail"] == "Cliente no encontrado"

    def test_endpoint_web_update_nonexistent_client_returns_404(self, client):
        form_data = {
            "name": "Fantasma",
            "email": "fantasma@test.com",
            "phone": "5500000000"
        }
        response = client.post("/clients/99999/edit", data=form_data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Cliente no encontrado"

    def test_endpoint_web_delete_nonexistent_client_redirects_with_error(self, client):
        response = client.post("/clients/99999/delete", follow_redirects=False)
        assert response.status_code == 303
        assert "error=El+cliente+no+existe" in response.headers["location"]

    def test_endpoint_web_add_note_to_nonexistent_client_redirects_with_error(self, client):
        response = client.post("/clients/99999/notes", data={"content": "Nota test"}, follow_redirects=False)
        assert response.status_code == 303
        assert "error=Cliente+no+encontrado" in response.headers["location"]


class TestEndpointsDeletion:
    """Pruebas de endpoints para eliminación de clientes y notas."""

    def test_endpoint_api_delete_client_success_returns_204(self, client, sample_client_payload):
        create_res = client.post("/api/clients", json=sample_client_payload)
        client_id = create_res.json()["id"]

        del_res = client.delete(f"/api/clients/{client_id}")
        assert del_res.status_code == 204

        # Confirmar que ahora es 404
        get_res = client.get(f"/api/clients/{client_id}")
        assert get_res.status_code == 404

    def test_endpoint_api_delete_note_success_returns_204(self, client, sample_client_payload):
        create_res = client.post("/api/clients", json=sample_client_payload)
        client_id = create_res.json()["id"]

        note_res = client.post(f"/api/clients/{client_id}/notes", json={"content": "Nota a borrar"})
        note_id = note_res.json()["id"]

        del_note_res = client.delete(f"/api/notes/{note_id}")
        assert del_note_res.status_code == 204

    def test_endpoint_api_delete_nonexistent_note_returns_404(self, client):
        del_res = client.delete("/api/notes/99999")
        assert del_res.status_code == 404
        assert "no encontrada" in del_res.json()["detail"]

    def test_endpoint_web_delete_client_success_redirects(self, client, sample_client_payload):
        create_res = client.post("/api/clients", json=sample_client_payload)
        client_id = create_res.json()["id"]

        del_res = client.post(f"/clients/{client_id}/delete", follow_redirects=False)
        assert del_res.status_code == 303
        assert "msg=Cliente+eliminado+exitosamente" in del_res.headers["location"]

    def test_endpoint_web_delete_note_success_redirects(self, client, sample_client_payload):
        create_res = client.post("/api/clients", json=sample_client_payload)
        client_id = create_res.json()["id"]

        note_res = client.post(f"/api/clients/{client_id}/notes", json={"content": "Nota web a borrar"})
        note_id = note_res.json()["id"]

        del_res = client.post(f"/clients/{client_id}/notes/{note_id}/delete", follow_redirects=False)
        assert del_res.status_code == 303
        assert "msg=Nota+eliminada+exitosamente" in del_res.headers["location"]

    def test_endpoint_web_delete_nonexistent_note_redirects_with_error(self, client, sample_client_payload):
        create_res = client.post("/api/clients", json=sample_client_payload)
        client_id = create_res.json()["id"]

        del_res = client.post(f"/clients/{client_id}/notes/99999/delete", follow_redirects=False)
        assert del_res.status_code == 303
        assert "error=Nota+no+encontrada" in del_res.headers["location"]

    def test_endpoint_web_add_note_unexpected_exception_returns_422(self, client, sample_client_payload):
        create_res = client.post("/api/clients", json=sample_client_payload)
        client_id = create_res.json()["id"]

        # Simular una falla inesperada en create_note para cubrir el bloque except Exception
        with patch("app.services.create_note", side_effect=RuntimeError("Fallo inesperado de BD")):
            res = client.post(f"/clients/{client_id}/notes", data={"content": "Nota con error inesperado"})
            assert res.status_code == 422
            assert "Error al guardar la nota: Fallo inesperado de BD" in res.text
