from pathlib import Path
import os
import pytest
from playwright.sync_api import sync_playwright
HTML=(Path(__file__).resolve().parents[1]/'demo'/'form.html').read_text(encoding='utf-8')

@pytest.fixture
def page():
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True, **({"executable_path": os.environ["BROWSER_DEMO_CHROMIUM_PATH"]} if os.environ.get("BROWSER_DEMO_CHROMIUM_PATH") else {}))
        try:
            page=browser.new_page()
            page.set_content(HTML)
            yield page
        finally:
            browser.close()

def test_form_submission(page):
    page.get_by_label('Name').fill('Demo User')
    page.get_by_label('Task').select_option('report')
    page.get_by_role('button',name='Submit request').click()
    assert page.get_by_role('status').inner_text()=='Request accepted: Demo User / report'

def test_required_field_validation(page):
    page.get_by_role('button',name='Submit request').click()
    assert page.locator('#name').evaluate('(el) => el.validity.valueMissing')
    assert page.get_by_role('status').inner_text()==''

def test_transient_browser_timeout_recovers(page):
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from automation.retry import retry
    attempts=[]
    def fill_name():
        attempts.append(1)
        if len(attempts)==1: raise PlaywrightTimeoutError('Simulated temporary page delay')
        page.get_by_label('Name').fill('Recovered User')
        return page.get_by_label('Name').input_value()
    assert retry(fill_name,attempts=2,retry_on=(PlaywrightTimeoutError,))=='Recovered User'
    assert len(attempts)==2

def test_real_playwright_timeout_does_not_retry_unrelated_errors(page):
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from automation.retry import retry
    calls=[]
    def missing():
        calls.append(1)
        page.locator('#missing-element').wait_for(timeout=100)
    with pytest.raises(PlaywrightTimeoutError):
        retry(missing,attempts=2,retry_on=(PlaywrightTimeoutError,))
    assert len(calls)==2

def test_untrusted_name_is_rendered_as_text(page):
    payload='<img src=x onerror=alert(1)>'
    page.get_by_label('Name').fill(payload)
    page.get_by_role('button',name='Submit request').click()
    assert payload in page.get_by_role('status').inner_text()
    assert page.locator('#result img').count()==0
