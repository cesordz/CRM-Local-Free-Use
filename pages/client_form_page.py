from typing import Optional
from playwright.sync_api import Locator
from pages.base_page import BasePage


class ClientFormPage(BasePage):
    """Page Object para los formularios de Alta y Edición de Clientes."""

    def navigate_new(self):
        self.navigate_to("/clients/new")

    def navigate_edit(self, client_id: int):
        self.navigate_to(f"/clients/{client_id}/edit")

    # Locators
    @property
    def title(self) -> Locator:
        return self.page.locator('[data-testid="form-title"]')

    @property
    def name_input(self) -> Locator:
        return self.page.locator('[data-testid="input-client-name"]')

    @property
    def email_input(self) -> Locator:
        return self.page.locator('[data-testid="input-client-email"]')

    @property
    def phone_input(self) -> Locator:
        return self.page.locator('[data-testid="input-client-phone"]')

    @property
    def company_input(self) -> Locator:
        return self.page.locator('[data-testid="input-client-company"]')

    @property
    def submit_button(self) -> Locator:
        return self.page.locator('[data-testid="btn-submit-client"]')

    @property
    def cancel_button(self) -> Locator:
        return self.page.locator('[data-testid="btn-cancel-form"]')

    # Errores
    def error_locator(self, field: str) -> Locator:
        return self.page.locator(f'[data-testid="error-{field}"]')

    def get_field_error(self, field: str) -> Optional[str]:
        loc = self.error_locator(field)
        if loc.is_visible():
            return loc.inner_text().strip()
        return None

    # Acciones
    def fill_form(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        company: Optional[str] = None
    ):
        if name is not None:
            self.name_input.fill(name)
        if email is not None:
            self.email_input.fill(email)
        if phone is not None:
            self.phone_input.fill(phone)
        if company is not None:
            self.company_input.fill(company)

    def submit(self):
        self.submit_button.click()

    def fill_and_submit(
        self,
        name: str,
        email: str,
        phone: str,
        company: Optional[str] = None
    ):
        self.fill_form(name=name, email=email, phone=phone, company=company)
        self.submit()

    def get_input_value(self, field: str) -> str:
        mapping = {
            "name": self.name_input,
            "email": self.email_input,
            "phone": self.phone_input,
            "company": self.company_input
        }
        loc = mapping.get(field)
        if loc:
            return loc.input_value()
        return ""
