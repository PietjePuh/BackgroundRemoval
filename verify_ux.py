import time
import requests
from playwright.sync_api import sync_playwright


def verify_ux():
    # Wait for Streamlit
    print("Waiting for Streamlit...")
    for _ in range(30):
        try:
            resp = requests.get("http://localhost:8501/_stcore/health")
            if resp.status_code == 200:
                break
        except requests.ConnectionError:
            pass
        time.sleep(1)
    else:
        print("Timeout waiting for Streamlit")
        return

    print("Streamlit is up! Launching browser...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Emulate a desktop viewport
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()

        try:
            page.goto("http://localhost:8501")

            # Wait for main title to confirm app loaded
            # Increase timeout as rembg model loading might be slow on startup (can be > 2 mins)
            print("Waiting for app title...")
            page.wait_for_selector(
                "h1:has-text('Remove background from your image')", timeout=300000
            )

            # Find the "Custom Image" radio option in the sidebar
            print("Clicking 'Custom Image'...")
            # Use a locator that finds the text inside a label or span associated with the radio
            # Streamlit renders radio options as <label> elements containing the text
            # We use .first because sometimes text matches multiple elements
            custom_image_option = (
                page.locator("label").filter(has_text="Custom Image").first
            )
            custom_image_option.click()

            # Wait for the info message
            print("Waiting for info message...")
            info_message = "👆 Upload an image to use as background"
            page.wait_for_selector(f"text={info_message}", timeout=10000)

            print("Info message found! Taking screenshot...")
            page.screenshot(path="verification_screenshot.png")

        except Exception as e:
            print(f"Error during verification: {e}")
            page.screenshot(path="error_screenshot.png")
        finally:
            browser.close()


if __name__ == "__main__":
    verify_ux()
