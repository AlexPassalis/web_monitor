from playwright.sync_api import Browser


def get_html_content(browser: Browser, url: str) -> str:
    page = browser.new_page()
    page.goto(url, wait_until='domcontentloaded', timeout=60000)
    html_content = page.content()
    page.close()
    return html_content
