from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = (Path(__file__).resolve().parents[1] / "demo" / "form.html").as_uri()

def test_form_submission():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(PAGE)
            page.get_by_label("Name").fill("Demo User")
            page.get_by_label("Task").select_option("report")
            page.get_by_role("button", name="Submit request").click()
            assert page.get_by_role("status").inner_text() == "Request accepted: Demo User / report"
        finally:
            browser.close()

def test_required_field_validation():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(PAGE)
            page.get_by_role("button", name="Submit request").click()
            assert page.locator("#name").evaluate("(el) => el.validity.valueMissing")
            assert page.get_by_role("status").inner_text() == ""
        finally:
            browser.close()
