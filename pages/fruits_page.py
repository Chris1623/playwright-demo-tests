"""Page object for the API-mocking demo app: https://demo.playwright.dev/api-mocking

The page loads a list of fruits from a JSON API and renders their names.
"""

from playwright.sync_api import Locator, Page


class FruitsPage:
    PATH = "/api-mocking"
    API_ROUTE = "*/**/api/v1/fruits"  # glob for page.route() and page.expect_response()

    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self) -> "FruitsPage":
        self.page.goto(self.PATH)
        return self

    def fruit(self, name: str) -> Locator:
        return self.page.get_by_text(name, exact=True)
