"""Page objects: one class per page, holding its locators and user actions."""

from pages.docs_page import DocsHomePage
from pages.fruits_page import FruitsPage
from pages.todo_page import TodoPage

__all__ = ["DocsHomePage", "FruitsPage", "TodoPage"]
