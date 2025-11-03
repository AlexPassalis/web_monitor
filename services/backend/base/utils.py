from playwright.sync_api import Browser
import time


def get_html_content(browser: Browser, url: str) -> str:
    page = browser.new_page()
    page.goto(url, wait_until='networkidle', timeout=60000)
    html_content = page.content()

    screenshot_path = f'/app/screenshots/{url}_{int(time.time())}.png'
    page.screenshot(path=screenshot_path, full_page=True)

    page.close()
    return html_content
