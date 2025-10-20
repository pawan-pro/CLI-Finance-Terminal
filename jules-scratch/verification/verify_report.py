
from playwright.sync_api import sync_playwright
import subprocess
import os

def run_verification():
    # Step 1: Generate the report (already done by the workflow, but good to have)
    try:
        subprocess.run(['python', 'approach 2.0/daily_report-i.py'], check=True)
        print("Report generated successfully.")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error generating report: {e}")
        return

    # Step 2: Verify with Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Construct the absolute file path
        report_path = os.path.abspath('approach 2.0/daily_report-i.html')

        try:
            # Go to the local HTML file
            page.goto(f'file://{report_path}')

            # Give the page a moment to load any dynamic content
            page.wait_for_timeout(1000)

            # Take a screenshot
            screenshot_path = 'jules-scratch/verification/verification.png'
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"Screenshot saved to {screenshot_path}")

        except Exception as e:
            print(f"An error occurred during Playwright verification: {e}")

        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()
