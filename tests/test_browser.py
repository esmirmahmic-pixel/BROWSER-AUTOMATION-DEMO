from pathlib import Path
from playwright.sync_api import sync_playwright

HTML = (Path(__file__).resolve().parents[1] / "demo" / "form.html").read_text(encoding="utf-8")

def test_form_submission():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.set_content(HTML)
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
            page.set_content(HTML)
            page.get_by_role("button", name="Submit request").click()
            assert page.locator("#name").evaluate("(el) => el.validity.valueMissing")
            assert page.get_by_role("status").inner_text() == ""
        finally:
            browser.close()


def test_transient_browser_timeout_recovers():
    """First browser lookup times out, second attempt succeeds."""
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from automation.retry import retry

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.set_content(HTML)
            attempts = []

            def fill_name():
                attempts.append(1)
                if len(attempts) == 1:
                    # Deliberate transient failure for a deterministic demo.
                    raise PlaywrightTimeoutError("Simulated temporary page delay")
                page.get_by_label("Name").fill("Recovered User")
                return page.get_by_label("Name").input_value()

            result = retry(
                fill_name,
                attempts=2,
                retry_on=(PlaywrightTimeoutError,),
            )
            assert result == "Recovered User"
            assert len(attempts) == 2
        finally:
            browser.close()
