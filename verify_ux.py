from playwright.sync_api import sync_playwright


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Navigating to app...")
        try:
            page.goto("http://localhost:8501", timeout=60000)

            # Wait for the title with extended timeout
            print("Waiting for H1 title (up to 300s)...")
            page.wait_for_selector("h1", timeout=300000)
            print("App loaded.")

            # The app automatically processes the default image on load (zebra.jpg)
            # We need to wait for the download button to appear
            print("Waiting for processing (looking for 'Background Removed')...")
            # Processing might take time (rembg model download/init)
            # Wait for "Background Removed" header
            page.wait_for_selector("text=Background Removed", timeout=300000)

            # Find the download button
            # The button text should now contain "zebra_rmbg.png"
            print("Looking for download button...")

            # We can look for a button that contains the filename
            download_button = page.get_by_role("button", name="Download zebra_rmbg.png")

            # Wait for it to be visible
            download_button.wait_for(state="visible", timeout=30000)

            if download_button.is_visible():
                print("SUCCESS: Download button with filename found!")
                print(f"Button text: {download_button.inner_text()}")
            else:
                print("FAILURE: Download button with filename NOT found.")

            # Take screenshot
            page.screenshot(path="verification_screenshot.png", full_page=True)
            print("Screenshot saved to verification_screenshot.png")

        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="error_screenshot.png", full_page=True)
            print("Saved error_screenshot.png")
            print("Page content dump:")
            print(page.content())
        finally:
            browser.close()


if __name__ == "__main__":
    run()
