"""playwright.dev: a user journey and a broken-link check."""

import re

import pytest
from playwright.sync_api import Page, expect

from pages import DocsHomePage

pytestmark = pytest.mark.docs

# Broken links this suite has found on the live site. They're listed so the check stays
# green while they're open, and the test fails as soon as one is fixed, so the list stays current.
KNOWN_BROKEN_LINKS = {
    "https://playwright.dev/python/docs/getting-started-vscode",  # 404, found 2026-11-04
}


def test_get_started_leads_to_the_installation_guide(page: Page, docs_home: DocsHomePage):
    expect(page).to_have_title(re.compile("Playwright"))

    docs_home.get_started.click()

    expect(page).to_have_url(re.compile(r"/python/docs/intro"))
    expect(page.get_by_role("heading", name="Installation", level=1)).to_be_visible()


@pytest.mark.only_browser("chromium")  # link status doesn't depend on the browser
def test_docs_home_has_no_broken_internal_links(page: Page, docs_home: DocsHomePage):
    links = docs_home.internal_links()
    assert links, "found no internal links on the page"

    broken = {}
    for url in links:
        response = page.request.get(url, timeout=15_000)
        if response.status >= 400:
            broken[url] = response.status

    new_breaks = [f"{status}  {url}" for url, status in broken.items() if url not in KNOWN_BROKEN_LINKS]
    assert not new_breaks, f"{len(new_breaks)} of {len(links)} links are broken:\n" + "\n".join(new_breaks)

    now_fixed = (KNOWN_BROKEN_LINKS & set(links)) - broken.keys()
    assert not now_fixed, f"These links work again, remove them from KNOWN_BROKEN_LINKS: {sorted(now_fixed)}"
