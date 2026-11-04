"""Page object for the Playwright for Python docs home page: https://playwright.dev/python/"""

from urllib.parse import urldefrag

from playwright.sync_api import Page


class DocsHomePage:
    URL = "https://playwright.dev/python/"
    ORIGIN = "https://playwright.dev"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.get_started = page.get_by_role("link", name="Get started")

    def open(self) -> "DocsHomePage":
        self.page.goto(self.URL)
        return self

    def internal_links(self) -> list[str]:
        """Unique absolute URLs of every playwright.dev link on the page, without #fragments."""
        hrefs = self.page.locator("a[href]").evaluate_all("links => links.map(a => a.href)")
        return sorted(
            {urldefrag(href).url for href in hrefs if href.startswith(self.ORIGIN)}
        )
