"""Page object for the TodoMVC demo app: https://demo.playwright.dev/todomvc"""

import json
import re

from playwright.sync_api import Locator, Page


class TodoPage:
    PATH = "/todomvc"
    STORAGE_KEY = "react-todos"  # the app saves its todos in localStorage under this key

    def __init__(self, page: Page) -> None:
        self.page = page
        self.new_todo_input = page.get_by_placeholder("What needs to be done?")
        self.items = page.get_by_test_id("todo-item")
        self.titles = page.get_by_test_id("todo-title")
        self.counter = page.get_by_test_id("todo-count")
        self.toggle_all = page.get_by_label("Mark all as complete")
        self.clear_completed_button = page.get_by_role("button", name="Clear completed")

    # --- navigation -------------------------------------------------------

    def open(self) -> "TodoPage":
        self.page.goto(self.PATH)
        return self

    def filter_link(self, name: str) -> Locator:
        """One of the footer filters: 'All', 'Active' or 'Completed'."""
        return self.page.get_by_role("link", name=name, exact=True)

    # --- locators ---------------------------------------------------------

    def item(self, title: str) -> Locator:
        """The list item whose title is exactly `title`."""
        exact_title = self.page.get_by_test_id("todo-title").filter(
            has_text=re.compile(rf"^{re.escape(title)}$")
        )
        return self.items.filter(has=exact_title)

    # --- actions ----------------------------------------------------------

    def add(self, *titles: str) -> None:
        for title in titles:
            self.new_todo_input.fill(title)
            self.new_todo_input.press("Enter")

    def toggle(self, title: str) -> None:
        self.item(title).get_by_role("checkbox").check()

    def start_editing(self, title: str) -> Locator:
        """Double-click a todo and return its edit textbox."""
        item = self.item(title)
        item.dblclick()
        return item.get_by_role("textbox", name="Edit")

    def edit(self, title: str, new_title: str) -> None:
        editor = self.start_editing(title)
        editor.fill(new_title)
        editor.press("Enter")

    # --- localStorage -----------------------------------------------------

    def wait_for_stored(self, count: int, completed: int = 0) -> None:
        """Wait until localStorage holds `count` todos, `completed` of them done."""
        self.page.wait_for_function(
            """([key, count, completed]) => {
                const todos = JSON.parse(localStorage.getItem(key) || "[]");
                return todos.length === count
                    && todos.filter(t => t.completed).length === completed;
            }""",
            arg=[self.STORAGE_KEY, count, completed],
        )

    def stored_todos(self) -> list[dict]:
        raw = self.page.evaluate("key => localStorage.getItem(key)", self.STORAGE_KEY)
        return json.loads(raw) if raw else []
