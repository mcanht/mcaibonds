from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

def download_ibonds_with_all_bonds():
    # --- CONFIGURE YOUR DESTINATION FOLDER HERE ---
    target_folder = Path(r"C:\Users\nicholas\OneDrive - Maryland Capital Advisors\My Files\Desktop\Bond ETF's")
    target_folder.mkdir(parents=True, exist_ok=True)
    print(f"Files will be saved to: {target_folder}")

    with sync_playwright() as p:
        # Launch browser with a clean fixed viewport size
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = context.new_page()
        
        # Navigate to the BlackRock iBonds Ladder Tool page
        print("Navigating to BlackRock iBonds Ladder Tool...")
        page.goto("https://www.blackrock.com/us/financial-professionals/tools/ibonds")
        
        # --- HANDLE INITIAL COOKIE / CONSENT POPUP ---
        print("Checking for consent/cookie banner...")
        page.wait_for_timeout(2000)
        try:
            accept_btn = page.locator("button#onetrust-accept-btn-handler, button:has-text('Accept'), button:has-text('I Agree')").first
            if accept_btn.is_visible(timeout=5000):
                accept_btn.click(force=True)
                print("Successfully clicked the consent/accept button.")
                page.wait_for_timeout(1000)
            else:
                print("Consent button not immediately visible.")
        except Exception as e:
            print(f"Cookie banner handling notice: {e}")
        
        # Zoom out the web page to 75% so elements scale nicely within the custom window
        print("Zooming out webpage to 75%...")
        page.evaluate("document.body.style.zoom = '0.75'")
        page.wait_for_timeout(1500)
        
        # Wait for the 'BOND TYPE' section to load safely
        print("Waiting for 'BOND TYPE' filter section...")
        page.get_by_text("BOND TYPE", exact=True).wait_for(state="visible", timeout=20000)
        
        # List of bond types to ensure are selected
        bond_types = ["Corporate", "Treasury", "TIPS", "Municipal", "High Yield"]
        
        for bond in bond_types:
            label = page.locator(f"label:has-text('{bond}')")
            if label.count() > 0:
                try:
                    label.first.click(force=True)
                    print(f"Ensured selected: {bond}")
                except Exception as e:
                    print(f"Could not click {bond}: {e}")

        # Wait for the table data to process
        print("Waiting for table data to update...")
        page.wait_for_timeout(4000)
        
        # Switch over to "CUSTOMIZE LADDER" before downloading
        print("Clicking 'CUSTOMIZE LADDER' tab...")
        try:
            customize_tab = page.locator("text=CUSTOMIZE LADDER")
            customize_tab.first.wait_for(state="visible", timeout=10000)
            customize_tab.first.click(force=True)
            print("Successfully clicked 'CUSTOMIZE LADDER'")
            page.wait_for_timeout(2000)
        except Exception as e:
            print(f"Notice during customize ladder click: {e}")
        
        # Scroll down slightly to make sure the download button is fully inside the viewport
        print("Scrolling down to download button...")
        page.evaluate("window.scrollBy(0, 600)")
        page.wait_for_timeout(1000)
        
        # Locate the download button and trigger the file download event
        print("Locating and clicking 'DOWNLOAD XLS'...")
        download_btn = page.locator("text=DOWNLOAD XLS").first
        download_btn.wait_for(state="visible", timeout=15000)
        
        print("Triggering download...")
        with page.expect_download() as download_info:
            download_btn.click(force=True)
            
        download = download_info.value
        
        # Extract the original extension (e.g., .xls or .xlsx) and format today's date
        original_ext = Path(download.suggested_filename).suffix or ".xlsx"
        date_stamp = datetime.now().strftime("%m_%d_%y")
        file_name = f"yiel-table_{date_stamp}{original_ext}"
        destination_path = target_folder / file_name
        
        # Save the file into your OneDrive Bond ETF's folder
        download.save_as(destination_path)
        print(f"File successfully saved to: {destination_path}")

        browser.close()

if __name__ == "__main__":
    download_ibonds_with_all_bonds()