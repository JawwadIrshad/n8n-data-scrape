import time
import csv
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ========================
# Selenium Setup
# ========================
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# ========================
# CSV Setup
# ========================
FILE_NAME = "google_maps_data.csv"

# Create CSV with headers
with open(FILE_NAME, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Name", "Category", "Address", "Hours", "Phone"])


def save_to_csv(record):
    """Save one record to CSV"""
    with open(FILE_NAME, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            record["Name"],
            record["Category"],
            record["Address"],
            record["Hours"],
            record["Phone"]
        ])


def wait_for_loading_to_finish():
    """Wait for Google Maps spinner to disappear"""
    try:
        WebDriverWait(driver, 10).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.m6QErb.DxyBCb.kA9KIf.dS8AEf[aria-busy='true']"))
        )
    except TimeoutException:
        pass


def visible_scroll(scrollable_element):
    """Scroll through the Google Maps sidebar to load new results"""
    listings = driver.find_elements(By.CLASS_NAME, "Nv2PK")
    if listings:
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", listings[-1])
        time.sleep(random.uniform(2, 4))


def scrape_google_maps(keyword):
    """Scrape Google Maps results: Name, Category, Address, Hours, Phone"""
    print(f"\n🔍 Scraping keyword: {keyword}")
    url = f"https://www.google.com/maps/search/{keyword.replace(' ', '+')}"
    driver.get(url)
    time.sleep(5)

    results = []
    prev_len = 0
    stagnant_scrolls = 0
    max_stagnant_scrolls = 5

    # Dismiss cookie popup if exists
    try:
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept all') or contains(., 'I agree')]"))
        )
        cookie_button.click()
        time.sleep(2)
    except:
        pass

    # Sidebar container
    try:
        scrollable = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]'))
        )
    except TimeoutException:
        print("❌ Could not find results container.")
        return results

    # Scroll and scrape
    while stagnant_scrolls < max_stagnant_scrolls:
        wait_for_loading_to_finish()
        time.sleep(random.uniform(1.5, 3.5))

        listings = driver.find_elements(By.CLASS_NAME, "Nv2PK")

        for listing in listings[len(results):]:
            name, category, address, hours, phone = "", "", "", "", ""

            # Name
            try:
                name = listing.find_element(By.CLASS_NAME, "qBF1Pd").text
            except NoSuchElementException:
                pass

            # Category + Address
            try:
                details = listing.find_elements(By.CLASS_NAME, "W4Efsd")
                if len(details) > 0:
                    category = details[0].text
                if len(details) > 1:
                    address = details[1].text
            except:
                pass

            # Hours
            try:
                hours = listing.find_element(By.CLASS_NAME, "o0Svhf").text
            except NoSuchElementException:
                hours = ""

            # Phone
            try:
                phone = listing.find_element(By.CLASS_NAME, "UsdlK").text
            except NoSuchElementException:
                phone = ""

            record = {
                "Name": name,
                "Category": category,
                "Address": address,
                "Hours": hours,
                "Phone": phone
            }

            results.append(record)
            save_to_csv(record)
            print(f"✅ Saved: {record['Name']}")

        # Stop if no new listings loaded
        if len(listings) == prev_len:
            stagnant_scrolls += 1
            print(f"⏳ No new results ({stagnant_scrolls}/{max_stagnant_scrolls})")
        else:
            stagnant_scrolls = 0
        prev_len = len(listings)

        visible_scroll(scrollable)

    print("✅ Finished scraping results.")
    return results


if __name__ == "__main__":
    keywords = [
        "real estate in miami Florida",
        "real estate agent in miami Florida"
    ]

    for keyword in keywords:
        scrape_google_maps(keyword)
        if keyword != keywords[-1]:
            delay = random.randint(10, 20)
            print(f"⏳ Waiting {delay} seconds before next search...")
            time.sleep(delay)

    driver.quit()
