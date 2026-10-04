import pytest
from pages.client_form_page import ClientFormPage


class TestClientFormValidationE2E:
    """Pruebas E2E de validación de formularios y visualización de mensajes de error con Page Object Model."""

    def test_validation_error_empty_name(self, form_page: ClientFormPage):
        form_page.navigate_new()
        form_page.fill_and_submit(
            name="   ",
            email="test@valido.com",
            phone="5512345678"
        )
        # Verificar mensaje de error en pantalla
        error = form_page.get_field_error("name")
        assert error is not None
        assert "El nombre no puede estar vacío" in error

    @pytest.mark.parametrize("invalid_email", [
        "correo-sin-arroba.com",
        "usuario@",
        "@dominio.com",
        "usuario@dominio",
        "espacios en@correo.com"
    ])
    def test_validation_error_invalid_email_format(self, form_page: ClientFormPage, invalid_email):
        form_page.navigate_new()
        form_page.fill_and_submit(
            name="Nombre Válido",
            email=invalid_email,
            phone="5512345678"
        )
        error = form_page.get_field_error("email")
        assert error is not None
        assert "value is not a valid email address" in error.lower() or "correo" in error.lower()

    def test_validation_error_duplicate_email(self, form_page: ClientFormPage):
        # 1. Registrar primer cliente
        form_page.navigate_new()
        form_page.fill_and_submit(
            name="Cliente Original",
            email="duplicado@empresa.com",
            phone="5511111111"
        )

        # 2. Intentar registrar un segundo cliente con el mismo email
        form_page.navigate_new()
        form_page.fill_and_submit(
            name="Cliente Segundo",
            email="duplicado@empresa.com",
            phone="5522222222"
        )

        # 3. Validar mensaje de correo duplicado
        error = form_page.get_field_error("email")
        assert error is not None
        assert "ya está registrado" in error

    @pytest.mark.parametrize("invalid_phone", [
        "123456789",          # 9 dígitos (límite inferior)
        "12345678901",        # 11 dígitos (límite superior)
        "12345abc90",         # Letras
        "55-1234-56",         # Guiones
        "!@#$%^&*()",         # Símbolos
        "          "          # Espacios
    ])
    def test_validation_error_phone_boundary_and_type(self, form_page: ClientFormPage, invalid_phone):
        form_page.navigate_new()
        form_page.fill_and_submit(
            name="Tester Teléfono",
            email="telefono@valido.com",
            phone=invalid_phone
        )
        error = form_page.get_field_error("phone")
        assert error is not None
        assert "El teléfono debe contener exactamente 10 dígitos numéricos." in error

    def test_form_preserves_entered_values_on_validation_failure(self, form_page: ClientFormPage):
        # Si el usuario se equivoca en un campo, los demás campos deben mantenerse intactos
        form_page.navigate_new()
        form_page.fill_and_submit(
            name="Usuario Preservado",
            email="preservado@empresa.com",
            phone="999",  # Teléfono erróneo de 3 dígitos
            company="Empresa Preservada"
        )

        assert form_page.get_field_error("phone") is not None
        # Verificar que los otros campos retengan su valor
        assert form_page.get_input_value("name") == "Usuario Preservado"
        assert form_page.get_input_value("email") == "preservado@empresa.com"
        assert form_page.get_input_value("company") == "Empresa Preservada"
