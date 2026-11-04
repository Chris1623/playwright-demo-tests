"""TodoMVC: completing todos, filters, browser history and persistence."""

import re

import pytest
from playwright.sync_api import Page, expect

from pages import TodoPage

pytestmark = pytest.mark.todomvc

COMPLETED = re.compile(r"\bcompleted\b")
SELECTED = re.compile(r"\bselected\b")


def test_completing_a_todo_updates_the_counter(todo_page: TodoPage):
    todo_page.add("Buy milk", "Walk the dog")

    todo_page.toggle("Buy milk")

    expect(todo_page.item("Buy milk")).to_have_class(COMPLETED)
    expect(todo_page.item("Walk the dog")).not_to_have_class(COMPLETED)
    expect(todo_page.counter).to_have_text("1 item left")


def test_mark_all_as_complete_then_clear_completed(todo_page: TodoPage):
    todo_page.add("Buy milk", "Walk the dog", "Book flights")

    todo_page.toggle_all.check()
    expect(todo_page.items).to_have_class([COMPLETED] * 3)

    todo_page.clear_completed_button.click()
    expect(todo_page.items).to_have_count(0)
    expect(todo_page.clear_completed_button).to_be_hidden()


def test_filters_and_the_back_button(page: Page, todo_page: TodoPage):
    todo_page.add("Buy milk", "Walk the dog", "Book flights")
    todo_page.toggle("Walk the dog")

    todo_page.filter_link("Active").click()
    expect(page).to_have_url(re.compile(r"#/active$"))
    expect(todo_page.filter_link("Active")).to_have_class(SELECTED)
    expect(todo_page.titles).to_have_text(["Buy milk", "Book flights"])

    todo_page.filter_link("Completed").click()
    expect(page).to_have_url(re.compile(r"#/completed$"))
    expect(todo_page.titles).to_have_text(["Walk the dog"])

    page.go_back()
    expect(page).to_have_url(re.compile(r"#/active$"))
    expect(todo_page.titles).to_have_text(["Buy milk", "Book flights"])

    todo_page.filter_link("All").click()
    expect(todo_page.titles).to_have_count(3)


def test_todos_are_saved_and_survive_a_reload(page: Page, todo_page: TodoPage):
    todo_page.add("Buy milk", "Walk the dog")
    todo_page.toggle("Walk the dog")

    todo_page.wait_for_stored(count=2, completed=1)
    saved = [(t["title"], t["completed"]) for t in todo_page.stored_todos()]
    assert saved == [("Buy milk", False), ("Walk the dog", True)]

    page.reload()

    expect(todo_page.titles).to_have_text(["Buy milk", "Walk the dog"])
    expect(todo_page.item("Walk the dog")).to_have_class(COMPLETED)
    expect(todo_page.counter).to_have_text("1 item left")
