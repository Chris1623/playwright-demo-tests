"""API-mocking demo: intercepting, faking and inspecting network traffic."""

import pytest
from playwright.sync_api import Page, Route, expect

from pages import FruitsPage

pytestmark = pytest.mark.api_mocking


def test_page_shows_fake_data_from_a_mocked_api(page: Page, fruits_page: FruitsPage):
    fake_fruits = [{"name": "Strawberry", "id": 21}, {"name": "Dragon fruit", "id": 22}]
    page.route(FruitsPage.API_ROUTE, lambda route: route.fulfill(json=fake_fruits))

    fruits_page.open()

    for fruit in fake_fruits:
        expect(fruits_page.fruit(fruit["name"])).to_be_visible()


def test_real_response_can_be_modified_on_the_fly(page: Page, fruits_page: FruitsPage):
    real_names: list[str] = []

    def add_a_fruit(route: Route) -> None:
        response = route.fetch()  # let the real request go through
        fruits = response.json()
        real_names.extend(fruit["name"] for fruit in fruits)
        fruits.append({"name": "Loquat", "id": 100})
        route.fulfill(response=response, json=fruits)

    page.route(FruitsPage.API_ROUTE, add_a_fruit)

    fruits_page.open()

    expect(fruits_page.fruit("Loquat")).to_be_visible()
    assert real_names, "the real API returned no fruits"
    for name in real_names:
        expect(fruits_page.fruit(name)).to_be_visible()


def test_page_shows_exactly_what_the_real_api_returns(page: Page, fruits_page: FruitsPage):
    with page.expect_response(FruitsPage.API_ROUTE) as response_info:
        fruits_page.open()
    response = response_info.value

    # Contract checks on the API response
    assert response.ok, f"API answered {response.status}"
    fruits = response.json()
    assert isinstance(fruits, list) and fruits, "expected a non-empty list"
    for fruit in fruits:
        assert isinstance(fruit.get("name"), str) and fruit["name"].strip(), fruit
        assert isinstance(fruit.get("id"), int), fruit
    assert len({fruit["id"] for fruit in fruits}) == len(fruits), "fruit ids are not unique"

    # Every fruit the API returned is on the page
    for fruit in fruits:
        expect(fruits_page.fruit(fruit["name"])).to_be_visible()
