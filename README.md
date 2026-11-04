# Playwright Demo Tests

[![Playwright tests](https://github.com/Chris1623/playwright-demo-tests/actions/workflows/tests.yml/badge.svg)](https://github.com/Chris1623/playwright-demo-tests/actions/workflows/tests.yml)

End-to-end tests for Playwright's own demo websites, written in **Python** with **Playwright** and **pytest**.
15 focused tests run in Chromium, Firefox and WebKit on every push via GitHub Actions.

## What's tested

| Site | Tests | What they cover |
|---|---|---|
| [TodoMVC demo](https://demo.playwright.dev/todomvc) | 10 | Adding todos, ignoring blank input and trimming text, editing (double-click, Escape to cancel, clearing to delete), completing, "mark all", "clear completed", filters with URL routing and the back button, and saving to localStorage across a reload |
| [API-mocking demo](https://demo.playwright.dev/api-mocking) | 3 | Replacing the API with fake data, changing the real response on the fly, and checking the real API's response format and that the page shows exactly what it returned |
| [playwright.dev](https://playwright.dev/python/) | 2 | The "Get started" journey, and a check that no internal link on the docs home page is broken |

## Playwright techniques used

- **User-facing locators**: role, label, placeholder and test id. No CSS or XPath tied to page layout.
- **Web-first assertions** (`expect`) that retry until the page is ready. No `sleep()` anywhere.
- **Page Object Model**: each page's locators and actions live in one class under `pages/`, and pytest fixtures hand them to the tests.
- **Network interception**:
  - `route.fulfill()` returns fake JSON.
  - `route.fetch()` lets the real request through so the test can modify the response.
  - `expect_response()` captures real traffic so the test can check it.
- **API requests from tests**: `page.request` checks link status codes without opening each page.
- **Browser state**: the tests read localStorage, wait for a JavaScript condition with `wait_for_function`, reload the page, and use history with `go_back`.
- **Cross-browser runs**: a CI matrix covers three browsers. One test that doesn't depend on the browser is limited to Chromium with `only_browser`.
- **Debugging failures**: traces and screenshots are kept for failed tests, and every run produces an HTML report.

## Project structure

```
├── pages/                      # Page objects
│   ├── todo_page.py
│   ├── fruits_page.py
│   └── docs_page.py
├── tests/
│   ├── conftest.py             # Fixtures that open pages
│   ├── test_todo_add_edit.py
│   ├── test_todo_complete_filter.py
│   ├── test_api_mocking.py
│   └── test_playwright_dev.py
├── .github/workflows/tests.yml # CI: 3 browsers, on push, pull request and weekly
├── pytest.ini                  # Base URL, tracing, reports, markers
└── requirements.txt
```

## Running locally

Requires Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install                 # downloads the browsers
pytest
```

Useful options:

```bash
pytest --browser firefox                          # another browser
pytest --browser chromium --browser webkit        # several browsers in one run
pytest --headed --slowmo 500                      # watch the browser while tests run
pytest -m api_mocking                             # one area: todomvc, api_mocking or docs
pytest -k "edit"                                  # tests whose name matches
```

**Reports:** open `reports/report.html` after a run. For a failed test, open its trace to step through every action with DOM snapshots and network calls:

```bash
playwright show-trace test-results/<failed-test-folder>/trace.zip
```

## Continuous integration

GitHub Actions runs the suite in all three browsers on every push and pull request. It also runs every Monday morning, because the sites under test are live and can change. Each run attaches the HTML report, and when a test fails, its trace and screenshot as well.

## Notes on a few decisions

- **The link check found a real broken link.** On 4 November 2026, the Python docs home page linked to a page that returns 404. The link is recorded in `KNOWN_BROKEN_LINKS`, which keeps CI green while the problem is open. The test fails once the link works again, as a reminder to remove it from the list.

- **Every test is independent.** Each one gets a fresh browser context, so there's no shared state and the order doesn't matter.
- **The trimming test checks saved data, not the screen.** `to_have_text()` normalises whitespace, so it would pass even if the app didn't trim. Reading localStorage checks the actual stored value.
- **Network routes are registered before navigation.** That's why the `fruits_page` fixture doesn't open the page itself, unlike the other fixtures.
