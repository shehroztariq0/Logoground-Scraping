import os
import time
import re
import requests
import traceback
from openpyxl import Workbook
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Setup Chrome WebDriver
options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.maximize_window()
wb = Workbook()
ws = wb.active
ws.append(["title", "original_img_name", "description", "tags_str"])  # Optional: headers

start_url_base = "https://www.logoground.com/logos.php?search=&limit=favorites&currentpage={}"
current_page = 1
max_pages = 1000

def shorten_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

while current_page <= max_pages:
    page_url = start_url_base.format(current_page)
    print(f"📄 Scraping page {current_page}: {page_url}")
    driver.get(page_url)
    time.sleep(3)

    logo_items = driver.find_elements(By.CLASS_NAME, "logowrap")
    print(f"🖼️ Found {len(logo_items)} logos on page {current_page}.")

    if not logo_items:
        print("✅ No more logos found. Exiting.")
        break

    for item in logo_items:
        try:
            title = item.find_element(By.CLASS_NAME, "logopositioning3_title").text.strip().split("\n")[0]
            detail_link = item.find_element(By.CSS_SELECTOR, ".logopositioning2 a").get_attribute("href")

            # Open detail page
            driver.execute_script("window.open(arguments[0]);", detail_link)
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(2)

            # Parse full-size image from detail page using BeautifulSoup
            soup = BeautifulSoup(driver.page_source, "html.parser")
            full_img_elem = soup.find("img", class_="image_resize_mainlogo")
            if full_img_elem:
                full_img_url = full_img_elem["src"]
                if not full_img_url.startswith("http"):
                    full_img_url = "https://www.logoground.com/" + full_img_url

                original_img_name = shorten_filename(os.path.basename(full_img_url))
                img_path = os.path.join("images2", original_img_name)

                if not os.path.exists("images2"):
                    os.makedirs("images2")

                if not os.path.exists(img_path):
                    response = requests.get(full_img_url, headers={"User-Agent": "Mozilla/5.0"})
                    if response.status_code == 200:
                        with open(img_path, "wb") as f:
                            f.write(response.content)
                        print(f"✅ Downloaded full image: {original_img_name}")
                    else:
                        print(f"❌ Failed to download full image: {original_img_name}")
                else:
                    print(f"⚠️ Full image already exists: {original_img_name}")
            else:
                print("❌ Full-size image not found.")
                original_img_name = "N/A"

            # Description
            try:
                description_elem = driver.find_element(By.XPATH, "//p[.//span[contains(text(),\"DESCRIPTION\")]]/span[2]")
                description = description_elem.text.strip()
            except:
                description = "No description found"

            # Tags
            try:
                tags_elem = driver.find_element(By.XPATH, "//p[.//span[contains(text(),\"TAGS\")]]/span[2]")
                tags_str = tags_elem.text.strip()
            except:
                tags_str = ""

            # Close detail tab
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            # Save data to Excel
            ws.append([title, original_img_name, description, tags_str])
            wb.save("titles2.xlsx")
            print(f"💾 Saved logo: {title}")

        except Exception as e:
            print(f"❗ Error processing logo: {e}")
            traceback.print_exc()
            try:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            except:
                pass
            continue

    current_page += 1

try:
    wb.save("titles.xlsx")
    print("🎉 Scraping completed.")
except Exception as e:
    print(f"❌ Final save failed: {e}")
