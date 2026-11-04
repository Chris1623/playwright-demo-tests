import pytest
from playwright.sync_api import Page, expect

from pages import DocsHomePage, FruitsPage, TodoPage

# The sites under test are public and remote, so allow more than the 5 s default.
expect.set_options(timeout=10_000)


@pytest.fixture
def todo_page(page: Page) -> TodoPage:
    """TodoMVC, already open. Each test gets a fresh browser context, so the list starts empty."""
    return TodoPage(page).open()


@pytest.fixture
def fruits_page(page: Page) -> FruitsPage:
    """Not opened yet: tests register their network routes before navigating."""
    return FruitsPage(page)


@pytest.fixture
def docs_home(page: Page) -> DocsHomePage:
    return DocsHomePage(page).open()
