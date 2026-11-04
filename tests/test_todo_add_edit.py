"""TodoMVC: adding and editing todos."""

import pytest
from playwright.sync_api import expect

from pages import TodoPage

pytestmark = pytest.mark.todomvc


def test_add_a_todo(todo_page: TodoPage):
    todo_page.add("Buy milk")

    expect(todo_page.titles).to_have_text(["Buy milk"])
    expect(todo_page.counter).to_have_text("1 item left")
    expect(todo_page.new_todo_input).to_be_empty()


def test_todos_keep_the_order_they_were_added_in(todo_page: TodoPage):
    todo_page.add("Buy milk", "Walk the dog", "Book flights")

    expect(todo_page.titles).to_have_text(["Buy milk", "Walk the dog", "Book flights"])
    expect(todo_page.counter).to_have_text("3 items left")


def test_blank_todos_are_ignored_and_text_is_trimmed(todo_page: TodoPage):
    todo_page.add("     ")
    expect(todo_page.items).to_have_count(0)

    todo_page.add("   Walk the dog   ")
    expect(todo_page.items).to_have_count(1)

    # to_have_text() normalises whitespace, so check the saved data for the real value
    todo_page.wait_for_stored(count=1)
    assert todo_page.stored_todos()[0]["title"] == "Walk the dog"


def test_double_click_to_edit_a_todo(todo_page: TodoPage):
    todo_page.add("Buy milk", "Walk the dog")

    todo_page.edit("Buy milk", "Buy oat milk")

    expect(todo_page.titles).to_have_text(["Buy oat milk", "Walk the dog"])


def test_escape_cancels_an_edit(todo_page: TodoPage):
    todo_page.add("Buy milk")

    editor = todo_page.start_editing("Buy milk")
    editor.fill("Something else")
    editor.press("Escape")

    expect(editor).to_be_hidden()
    expect(todo_page.titles).to_have_text(["Buy milk"])


def test_clearing_the_text_while_editing_deletes_the_todo(todo_page: TodoPage):
    todo_page.add("Buy milk", "Walk the dog")

    todo_page.edit("Buy milk", "")

    expect(todo_page.titles).to_have_text(["Walk the dog"])
    expect(todo_page.counter).to_have_text("1 item left")
