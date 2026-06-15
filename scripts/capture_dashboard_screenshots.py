"""One-off helper to capture dashboard screenshots for the README.

Usage (with the dashboard already running):

    streamlit run app/dashboard.py --server.headless true --server.port 8765
    python scripts/capture_dashboard_screenshots.py

Not part of the production pipeline - safe to delete after use.
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "http://localhost:8765"
OUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "screenshots"

PAGES = [
    ("Pharmacovigilance signals (FAERS)", "faers.png"),
    ("Recall / manufacturing risk (Enforcement)", "enforcement.png"),
    ("Clinical trial risk & scenarios (ClinicalTrials.gov)", "clinicaltrials.png"),
    ("Sanctions screening (OFAC SDN)", "ofac.png"),
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.goto(URL)
        page.wait_for_selector("text=Pharmacovigilance Signal Detection", timeout=30000)

        for label, filename in PAGES:
            radio_option = page.locator("section[data-testid='stSidebar'] label", has_text=label)
            radio_option.click()
            page.wait_for_timeout(2500)
            page.locator(".js-plotly-plot").first.wait_for(state="visible", timeout=15000)
            page.wait_for_timeout(1500)
            page.screenshot(path=str(OUT_DIR / filename), full_page=True)
            print(f"Saved {OUT_DIR / filename}")

        browser.close()


if __name__ == "__main__":
    main()
