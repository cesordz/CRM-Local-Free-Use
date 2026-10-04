import pytest
from pages.client_list_page import ClientListPage
from pages.client_form_page import ClientFormPage
from pages.client_detail_page import ClientDetailPage


class TestClientCRUDFlowE2E:
    """Flujos de usuario completos (E2E) para el CRUD de clientes usando Page Object Model."""

    def test_create_client_successfully(self, list_page: ClientListPage, form_page: ClientFormPage, detail_page: ClientDetailPage):
        # 1. Navegar al directorio y verificar estado inicial
        list_page.navigate()
        assert list_page.title.inner_text() == "Directorio de Clientes"

        # 2. Hacer clic en Crear Cliente
        list_page.click_create_client()

        # 3. Llenar el formulario con datos válidos
        form_page.fill_and_submit(
            name="Mariana Fonseca",
            email="mariana.fonseca@empresa.com",
            phone="5512345678",
            company="Soluciones Cloud"
        )

        # 4. Verificar redirección automática a la ficha de detalle
        assert "Cliente #" in detail_page.client_title.inner_text()
        assert "Mariana Fonseca" in detail_page.client_title.inner_text()
        assert "mariana.fonseca@empresa.com" in detail_page.email_value.inner_text()
        assert "5512345678" in detail_page.phone_value.inner_text()
        assert "Soluciones Cloud" in detail_page.company_value.inner_text()

        # 5. Volver al directorio y verificar que aparezca en la tabla
        detail_page.back_button.click()
        assert list_page.has_client_name("Mariana Fonseca")

    def test_edit_client_successfully(self, list_page: ClientListPage, form_page: ClientFormPage, detail_page: ClientDetailPage):
        # 1. Crear cliente inicial
        form_page.navigate_new()
        form_page.fill_and_submit(
            name="Rodrigo Morales",
            email="rodrigo.inicial@test.com",
            phone="5599887766",
            company="Empresa Alfa"
        )

        # 2. Ir a editar desde la ficha de detalle
        detail_page.edit_button.click()

        # 3. Verificar que los campos vengan prellenados
        assert form_page.get_input_value("name") == "Rodrigo Morales"
        assert form_page.get_input_value("email") == "rodrigo.inicial@test.com"

        # 4. Modificar información
        form_page.fill_and_submit(
            name="Rodrigo Morales Actualizado",
            email="rodrigo.actual@test.com",
            phone="5500112233",
            company="Empresa Beta"
        )

        # 5. Verificar cambios en la vista de detalle
        assert "Rodrigo Morales Actualizado" in detail_page.client_title.inner_text()
        assert "rodrigo.actual@test.com" in detail_page.email_value.inner_text()
        assert "5500112233" in detail_page.phone_value.inner_text()
        assert "Empresa Beta" in detail_page.company_value.inner_text()

    def test_search_clients_by_name_flow(self, list_page: ClientListPage, form_page: ClientFormPage):
        # 1. Crear dos clientes de prueba
        form_page.navigate_new()
        form_page.fill_and_submit(name="Beatriz Paredes", email="beatriz@test.com", phone="1111111111")

        form_page.navigate_new()
        form_page.fill_and_submit(name="Carlos Santana", email="carlos@test.com", phone="2222222222")

        # 2. Ir al directorio
        list_page.navigate()
        assert list_page.has_client_name("Beatriz Paredes")
        assert list_page.has_client_name("Carlos Santana")

        # 3. Buscar "Beatriz"
        list_page.search("Beatriz")
        assert list_page.has_client_name("Beatriz Paredes")
        assert not list_page.has_client_name("Carlos Santana")

        # 4. Limpiar búsqueda
        list_page.clear_search()
        assert list_page.has_client_name("Beatriz Paredes")
        assert list_page.has_client_name("Carlos Santana")

        # 5. Búsqueda sin coincidencias
        list_page.search("NombreInexistenteXYZ")
        assert list_page.empty_state.is_visible()
        assert "No se encontraron resultados" in list_page.empty_state.inner_text()

    def test_delete_client_flow(self, list_page: ClientListPage, form_page: ClientFormPage):
        # 1. Crear cliente a eliminar
        form_page.navigate_new()
        form_page.fill_and_submit(name="Cliente Temporal", email="temporal@borrar.com", phone="5533333333")

        # 2. Ir a la lista y confirmar presencia
        list_page.navigate()
        assert list_page.has_client_name("Cliente Temporal")

        # 3. Obtener el enlace del cliente para identificar su ID
        client_link = list_page.page.locator('a[data-testid^="client-link-"]', has_text="Cliente Temporal")
        testid = client_link.get_attribute("data-testid")
        client_id = int(testid.replace("client-link-", ""))

        # 4. Eliminar aceptando el diálogo de confirmación
        list_page.click_delete_client(client_id, accept_confirm=True)

        # 5. Verificar mensaje de éxito y ausencia en la tabla
        assert list_page.has_client_name("Cliente Temporal") is False
        assert "Cliente eliminado exitosamente" in list_page.get_success_message()

    def test_add_and_delete_client_notes_flow(self, form_page: ClientFormPage, detail_page: ClientDetailPage):
        # 1. Crear cliente
        form_page.navigate_new()
        form_page.fill_and_submit(name="Héctor Lavoe", email="hector@salsa.com", phone="5544444444")

        # 2. Agregar nota de seguimiento
        note_text = "Primera llamada de prospección: cliente interesado en cotización."
        detail_page.add_note(note_text)

        # 3. Verificar que aparezca en el historial de notas
        notes = detail_page.get_all_notes()
        assert len(notes) == 1
        assert note_text in notes[0]

        # 4. Eliminar la nota
        delete_btn = detail_page.page.locator('[data-testid^="delete-note-"]').first
        note_id = int(delete_btn.get_attribute("data-testid").replace("delete-note-", ""))
        detail_page.delete_note(note_id, accept_confirm=True)

        # 5. Confirmar que se muestre el estado vacío de notas
        assert detail_page.empty_notes_state.is_visible()
