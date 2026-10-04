from typing import List, Optional
from playwright.sync_api import Locator
from pages.base_page import BasePage


class ClientDetailPage(BasePage):
    """Page Object para la ficha de detalle del cliente y gestión de notas (/clients/{id})."""

    def navigate(self, client_id: int):
        self.navigate_to(f"/clients/{client_id}")

    # Header Locators
    @property
    def client_title(self) -> Locator:
        return self.page.locator('[data-testid="client-detail-name"]')

    @property
    def back_button(self) -> Locator:
        return self.page.locator('[data-testid="back-to-clients-btn"]')

    @property
    def edit_button(self) -> Locator:
        return self.page.locator('[data-testid="edit-client-header-btn"]')

    @property
    def delete_button(self) -> Locator:
        return self.page.locator('[data-testid="delete-client-header-btn"]')

    # Info Locators
    @property
    def email_value(self) -> Locator:
        return self.page.locator('[data-testid="client-detail-email"]')

    @property
    def phone_value(self) -> Locator:
        return self.page.locator('[data-testid="client-detail-phone"]')

    @property
    def company_value(self) -> Locator:
        return self.page.locator('[data-testid="client-detail-company"]')

    # Notes Locators
    @property
    def note_textarea(self) -> Locator:
        return self.page.locator('[data-testid="input-note-content"]')

    @property
    def note_submit_btn(self) -> Locator:
        return self.page.locator('[data-testid="btn-submit-note"]')

    @property
    def note_error(self) -> Locator:
        return self.page.locator('[data-testid="error-note-content"]')

    @property
    def notes_list(self) -> Locator:
        return self.page.locator('[data-testid="notes-list"]')

    @property
    def empty_notes_state(self) -> Locator:
        return self.page.locator('[data-testid="empty-notes-state"]')

    # Acciones
    def add_note(self, content: str):
        self.note_textarea.fill(content)
        self.note_submit_btn.click()

    def get_note_error_message(self) -> Optional[str]:
        if self.note_error.is_visible():
            return self.note_error.inner_text().strip()
        return None

    def delete_note(self, note_id: int, accept_confirm: bool = True):
        if accept_confirm:
            self.page.once("dialog", lambda dialog: dialog.accept())
        else:
            self.page.once("dialog", lambda dialog: dialog.dismiss())
        self.page.locator(f'[data-testid="delete-note-{note_id}"]').click()

    def get_all_notes(self) -> List[str]:
        return self.page.locator('[data-testid^="note-text-"]').all_inner_texts()

    def click_delete_client(self, accept_confirm: bool = True):
        if accept_confirm:
            self.page.once("dialog", lambda dialog: dialog.accept())
        else:
            self.page.once("dialog", lambda dialog: dialog.dismiss())
        self.delete_button.click()
