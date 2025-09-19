import time
import csv
import re
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# ==========================
# Selenium Setup
# ==========================
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# ==========================
# CSV Setup
# ==========================
RESULT_FILE = "business_details.csv"
with open(RESULT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Name", "Address", "Phone", "Website", "Emails"])

# ==========================
# Step 1: Scrape business details from Google Maps
# ==========================
def scrape_from_google_maps(keyword):
    print(f"\n🔍 Searching: {keyword}")
    url = f"https://www.google.com/maps/search/{keyword.replace(' ', '+')}"
    driver.get(url)
    time.sleep(5)

    businesses = []
    prev_len = 0
    stagnant_scrolls = 0
    max_stagnant = 5

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]'))
        )
    except TimeoutException:
        print("❌ Could not find results container.")
        return businesses

    while stagnant_scrolls < max_stagnant:
        listings = driver.find_elements(By.CLASS_NAME, "Nv2PK")

        for listing in listings[len(businesses):]:
            try:
                listing.click()
                time.sleep(3)

                # Name
                try:
                    name = driver.find_element(By.CLASS_NAME, "DUwDvf").text.strip()
                except NoSuchElementException:
                    name = ""

                # Address
                try:
                    address = driver.find_element(By.XPATH, '//button[@data-item-id="address"]').text.strip()
                except NoSuchElementException:
                    address = ""

                # Phone (with multiple fallbacks)
# Phone (robust scraping with multiple fallbacks)
                phone = ""
                phone_raw = ""

                try:
                    # Standard phone button
                    phone_raw = driver.find_element(By.XPATH, '//button[@data-item-id="phone"]').text.strip()
                except NoSuchElementException:
                    try:
                        # Some results use <a href="tel:...">
                        phone_el = driver.find_element(By.XPATH, '//a[starts-with(@href, "tel:")]')
                        phone_raw = phone_el.get_attribute("href").replace("tel:", "").strip()
                    except NoSuchElementException:
                        try:
                            # Fallback: spans containing numbers
                            phone_raw = driver.find_element(By.XPATH, '//span[contains(text(), "+")]').text.strip()
                        except NoSuchElementException:
                            try:
                                phone_raw = driver.find_element(By.XPATH, '//span[contains(text(), "(")]').text.strip()
                            except NoSuchElementException:
                                phone_raw = ""

                # Normalize phone number
                if phone_raw:
                    phone_digits = re.sub(r"\D", "", phone_raw)  # keep only digits
                    if len(phone_digits) >= 8:
                        phone = phone_digits
                    else:
                        phone = phone_raw


                # Website
                try:
                    website_el = driver.find_element(By.XPATH, '//a[@data-item-id="authority"]')
                    website_url = website_el.get_attribute("href")
                except NoSuchElementException:
                    website_url = ""

                if website_url:  # Only keep if website exists
                    businesses.append({
                        "name": name,
                        "address": address,
                        "phone": phone,
                        "website": website_url
                    })
                    print(f"✅ Found: {name} | {website_url} | Phone: {phone}")

            except Exception:
                continue

        # stop condition
        if len(listings) == prev_len:
            stagnant_scrolls += 1
        else:
            stagnant_scrolls = 0
        prev_len = len(listings)

        if listings:
            driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth', block:'end'});", listings[-1])
            time.sleep(random.uniform(2, 4))

    print(f"✅ Total businesses with websites: {len(businesses)}")
    return businesses

# ==========================
# Step 2: Scrape emails from websites
# ==========================
def scrape_emails_from_websites(businesses):
    for biz in businesses:
        website = biz["website"]
        print(f"\n🌐 Visiting website: {website}")
        emails = []

        try:
            driver.get(website)
            time.sleep(random.uniform(5, 8))

            page_text = driver.find_element(By.TAG_NAME, "body").text
            found_emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", page_text)
            emails = list(set(found_emails))

        except Exception as e:
            print(f"❌ Failed to open {website}: {e}")

        # Save results
        with open(RESULT_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([biz["name"], biz["address"], biz["phone"], biz["website"], ", ".join(emails)])

        print(f"✅ Saved {biz['name']} | Emails: {len(emails)}")

# ==========================
# Main
# ==========================
if __name__ == "__main__":
    keywords = [
        # "real estate in miami Florida",
        "real estate agent in miami Florida",
        "estate agent in miami Florida",
        # "estate in miami Florida",
        # "agent in miami Florida"
    ]

    all_businesses = []
    for keyword in keywords:
        results = scrape_from_google_maps(keyword)
        all_businesses.extend(results)
        time.sleep(random.randint(5, 10))

    scrape_emails_from_websites(all_businesses)

    driver.quit()
    print("\n🎯 Scraping complete!")
