from typing import Optional
from playwright.sync_api import Page, Locator


class BasePage:
    """Clase base para todos los Page Objects del CRM."""

    def __init__(self, page: Page, base_url: str = "http://127.0.0.1:8000"):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def navigate_to(self, path: str = ""):
        target = f"{self.base_url}/{path.lstrip('/')}"
        self.page.goto(target)

    @property
    def alert_success(self) -> Locator:
        return self.page.locator('[data-testid="alert-success"]')

    @property
    def alert_error(self) -> Locator:
        return self.page.locator('[data-testid="alert-error"]')

    def get_success_message(self) -> Optional[str]:
        if self.alert_success.is_visible():
            return self.alert_success.inner_text().strip()
        return None

    def get_error_message(self) -> Optional[str]:
        if self.alert_error.is_visible():
            return self.alert_error.inner_text().strip()
        return None

    def click_nav_directory(self):
        self.page.locator('[data-testid="nav-clients-link"]').click()

    def click_nav_new_client(self):
        self.page.locator('[data-testid="nav-new-client-btn"]').click()
