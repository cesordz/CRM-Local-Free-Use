from typing import List
from playwright.sync_api import Locator
from pages.base_page import BasePage


class ClientListPage(BasePage):
    """Page Object para la pantalla de Directorio de Clientes (/clients)."""

    def navigate(self):
        self.navigate_to("/clients")

    # Locators
    @property
    def title(self) -> Locator:
        return self.page.locator('[data-testid="page-title"]')

    @property
    def new_client_btn(self) -> Locator:
        return self.page.locator('[data-testid="add-client-btn"]')

    @property
    def search_input(self) -> Locator:
        return self.page.locator('[data-testid="search-input"]')

    @property
    def search_submit_btn(self) -> Locator:
        return self.page.locator('[data-testid="search-submit-btn"]')

    @property
    def search_clear_btn(self) -> Locator:
        return self.page.locator('[data-testid="search-clear-btn"]')

    @property
    def table(self) -> Locator:
        return self.page.locator('[data-testid="clients-table"]')

    @property
    def table_rows(self) -> Locator:
        return self.page.locator('[data-testid="clients-table-body"] tr')

    @property
    def empty_state(self) -> Locator:
        return self.page.locator('[data-testid="empty-clients-state"]')

    # Acciones
    def search(self, name: str):
        self.search_input.fill(name)
        self.search_submit_btn.click()

    def clear_search(self):
        if self.search_clear_btn.is_visible():
            self.search_clear_btn.click()

    def click_create_client(self):
        self.new_client_btn.click()

    def get_row(self, client_id: int) -> Locator:
        return self.page.locator(f'[data-testid="client-row-{client_id}"]')

    def click_view_client(self, client_id: int):
        self.page.locator(f'[data-testid="view-client-{client_id}"]').click()

    def click_edit_client(self, client_id: int):
        self.page.locator(f'[data-testid="edit-client-{client_id}"]').click()

    def click_delete_client(self, client_id: int, accept_confirm: bool = True):
        # Escuchar y aceptar/rechazar el modal nativo confirm()
        if accept_confirm:
            self.page.once("dialog", lambda dialog: dialog.accept())
        else:
            self.page.once("dialog", lambda dialog: dialog.dismiss())

        self.page.locator(f'[data-testid="delete-client-{client_id}"]').click()

    def has_client_name(self, name: str) -> bool:
        return self.page.locator(f'[data-testid="clients-table-body"]', has_text=name).is_visible()

    def get_all_client_names(self) -> List[str]:
        return self.page.locator('[data-testid^="client-link-"]').all_inner_texts()
