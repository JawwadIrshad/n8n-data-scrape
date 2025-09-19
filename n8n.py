# import time
# import requests
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys

# # ========================
# # Airtable Config
# # ========================
# AIRTABLE_API_KEY = "__n8n_BLANK_VALUE_e5362baf-c777-4d57-a609-6eaf1f9e87f6"
# BASE_ID = "appykEGu0hnErZsKy"
# TABLE_NAME = "voicemail"

# AIRTABLE_ENDPOINT = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
# HEADERS = {"Authorization": f"Bearer {AIRTABLE_API_KEY}", "Content-Type": "application/json"}

# # ========================
# # Selenium Setup
# # ========================
# options = webdriver.ChromeOptions()
# options.add_argument("--start-maximized")
# driver = webdriver.Chrome(options=options)

# def save_to_airtable(record):
#     """Save scraped record to Airtable"""
#     data = {"fields": record}
#     response = requests.post(AIRTABLE_ENDPOINT, headers=HEADERS, json=data)
#     if response.status_code == 200:
#         print(f"✅ Saved: {record['Name']}")
#     else:
#         print(f"❌ Failed to save: {response.text}")

# def scrape_google_maps(keyword, max_results=20):
#     """Scrape Google Maps for a given keyword"""
#     url = f"https://www.google.com/maps/search/{keyword.replace(' ', '+')}"
#     driver.get(url)
#     time.sleep(5)

#     results = []
#     scroll_count = 0

#     while len(results) < max_results and scroll_count < 20:
#         time.sleep(3)

#         listings = driver.find_elements(By.CLASS_NAME, "Nv2PK")  # Each business card

#         for listing in listings[len(results):]:
#             try:
#                 name = listing.find_element(By.CLASS_NAME, "qBF1Pd").text
#             except:
#                 name = ""

#             try:
#                 rating = listing.find_element(By.CLASS_NAME, "MW4etd").text
#             except:
#                 rating = ""

#             try:
#                 category = listing.find_element(By.CLASS_NAME, "W4Efsd").text
#             except:
#                 category = ""

#             try:
#                 address = listing.find_element(By.CLASS_NAME, "W4Efsd:nth-child(2)").text
#             except:
#                 address = ""

#             record = {
#                 "Name": name,
#                 "Category": category,
#                 "Rating": rating,
#                 "Address": address
#             }

#             results.append(record)
#             save_to_airtable(record)

#             if len(results) >= max_results:
#                 break

#         # Scroll to load more results
#         scrollable = driver.find_element(By.CLASS_NAME, "m6QErb.DxyBCb.kA9KIf.dS8AEf")
#         driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable)
#         scroll_count += 1

#     return results

# if __name__ == "__main__":
#     keyword = "real estate"
#     results = scrape_google_maps(keyword, max_results=30)
#     print(f"✅ Scraped {len(results)} results")
#     driver.quit()


# import time
# import csv
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import NoSuchElementException

# # ========================
# # Selenium Setup
# # ========================
# options = webdriver.ChromeOptions()
# options.add_argument("--start-maximized")
# driver = webdriver.Chrome(options=options)

# # ========================
# # CSV Setup
# # ========================
# RAW_FILE = "google_maps_raw.csv"
# CLEAN_FILE = "google_maps_clean.csv"

# # Create RAW CSV with headers (overwrite if exists)
# with open(RAW_FILE, mode="w", newline="", encoding="utf-8") as file:
#     writer = csv.writer(file)
#     writer.writerow(["Name", "Category", "Rating", "Address"])

# def save_to_csv(record, filename):
#     """Save record to CSV file"""
#     with open(filename, mode="a", newline="", encoding="utf-8") as file:
#         writer = csv.writer(file)
#         writer.writerow([record["Name"], record["Category"], record["Rating"], record["Address"]])

# def scrape_google_maps(keyword):
#     """Scrape ALL Google Maps results for a given keyword"""
#     print(f"\n🔍 Scraping: {keyword}")
#     url = f"https://www.google.com/maps/search/{keyword.replace(' ', '+')}"
#     driver.get(url)
#     time.sleep(15)

#     results = []
#     prev_len = 0
#     stagnant_scrolls = 0  # Count when no new results appear

#     # Keep scrolling until no more new results
#     while True:
#         time.sleep(3)

#         listings = driver.find_elements(By.CLASS_NAME, "Nv2PK")  # Each business card

#         # Loop through NEW listings only
#         for listing in listings[len(results):]:
#             try:
#                 name = listing.find_element(By.CLASS_NAME, "qBF1Pd").text
#             except NoSuchElementException:
#                 name = ""

#             try:
#                 rating = listing.find_element(By.CLASS_NAME, "MW4etd").text
#             except NoSuchElementException:
#                 rating = ""

#             try:
#                 details = listing.find_elements(By.CLASS_NAME, "W4Efsd")
#                 category = details[0].text if len(details) > 0 else ""
#                 address = details[1].text if len(details) > 1 else ""
#             except:
#                 category, address = "", ""

#             record = {
#                 "Name": name,
#                 "Category": category,
#                 "Rating": rating,
#                 "Address": address
#             }

#             results.append(record)
#             save_to_csv(record, RAW_FILE)
#             print(f"✅ Saved: {record['Name']}")

#         # Stop if no new results
#         if len(listings) == prev_len:
#             stagnant_scrolls += 1
#             if stagnant_scrolls >= 3:  # Try a few times before stopping
#                 print("✅ No more results to load.")
#                 break
#         else:
#             stagnant_scrolls = 0
#         prev_len = len(listings)

#         # Scroll down to load more results
#         try:
#             scrollable = driver.find_element(By.CLASS_NAME, "m6QErb.DxyBCb.kA9KIf.dS8AEf")
#             driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable)
#         except:
#             print("⚠️ Could not scroll further.")
#             break

#     return results

# def remove_duplicates(input_file, output_file):
#     """Remove duplicate rows based on Name + Address"""
#     seen = set()
#     clean_rows = []

#     with open(input_file, mode="r", encoding="utf-8") as infile:
#         reader = csv.DictReader(infile)
#         for row in reader:
#             key = (row["Name"], row["Address"])
#             if key not in seen:
#                 seen.add(key)
#                 clean_rows.append(row)

#     # Write clean file
#     with open(output_file, mode="w", newline="", encoding="utf-8") as outfile:
#         writer = csv.DictWriter(outfile, fieldnames=["Name", "Category", "Rating", "Address"])
#         writer.writeheader()
#         writer.writerows(clean_rows)

#     print(f"\n✨ Cleaned data saved: {len(clean_rows)} unique results")

# if __name__ == "__main__":
#     keywords = [
#         "real estate in miami Florida",
#         "real estate agent in miami Florida",
#         "estate agent in miami Florida",
#         "estate in miami Florida",
#         "agent in miami Florida"
#     ]

#     all_results = []
#     for keyword in keywords:
#         results = scrape_google_maps(keyword)
#         all_results.extend(results)

#     driver.quit()

#     # Remove duplicates after scraping
#     remove_duplicates(RAW_FILE, CLEAN_FILE)




# import time
# import csv
# import random
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import NoSuchElementException, TimeoutException
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # ========================
# # Selenium Setup
# # ========================
# options = webdriver.ChromeOptions()
# options.add_argument("--start-maximized")
# # Add additional options to make browser less detectable
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)
# driver = webdriver.Chrome(options=options)
# driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# # ========================
# # CSV Setup
# # ========================
# RAW_FILE = "google_maps_raw.csv"
# CLEAN_FILE = "google_maps_clean.csv"

# # Create RAW CSV with headers (overwrite if exists)
# with open(RAW_FILE, mode="w", newline="", encoding="utf-8") as file:
#     writer = csv.writer(file)
#     writer.writerow(["Name", "Category", "Rating", "Address"])

# def save_to_csv(record, filename):
#     """Save record to CSV file"""
#     with open(filename, mode="a", newline="", encoding="utf-8") as file:
#         writer = csv.writer(file)
#         writer.writerow([record["Name"], record["Category"], record["Rating"], record["Address"]])

# def human_like_scroll(scrollable_element, driver):
#     """Simulate human-like scrolling behavior"""
#     # Get current scroll height
#     current_scroll = driver.execute_script("return arguments[0].scrollTop", scrollable_element)
#     scroll_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_element)
    
#     # Random scroll distance (between 300-800 pixels)
#     scroll_distance = random.randint(300, 800)
#     target_scroll = current_scroll + scroll_distance
    
#     # Don't scroll beyond the container
#     if target_scroll > scroll_height:
#         target_scroll = scroll_height
    
#     # Smooth scroll with multiple small steps
#     steps = random.randint(3, 8)
#     step_size = scroll_distance / steps
    
#     for i in range(steps):
#         # Add some randomness to each step
#         step_variation = random.randint(-20, 20)
#         current_step = current_scroll + (i * step_size) + step_variation
        
#         # Ensure we don't scroll beyond the container
#         if current_step > scroll_height:
#             current_step = scroll_height
            
#         driver.execute_script("arguments[0].scrollTop = arguments[1]", scrollable_element, current_step)
        
#         # Random pause between scroll steps
#         time.sleep(random.uniform(0.1, 0.3))
    
#     return target_scroll

# def wait_for_loading_to_finish():
#     """Wait for Google Maps 'loading' spinner to disappear"""
#     try:
#         # Spinner is usually inside the scrollable results container
#         WebDriverWait(driver, 10).until_not(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "div.m6QErb.DxyBCb.kA9KIf.dS8AEf[aria-busy='true']"))
#         )
#     except TimeoutException:
#         pass  # If timeout, just continue

# def scrape_google_maps(keyword):
#     """Scrape ALL Google Maps results for a given keyword"""
#     print(f"\n🔍 Scraping: {keyword}")
#     url = f"https://www.google.com/maps/search/{keyword.replace(' ', '+')}"
#     driver.get(url)
#     time.sleep(5)

#     results = []
#     prev_len = 0
#     stagnant_scrolls = 0
#     max_stagnant_scrolls = 5  # Increased to handle slower loading

#     # Try to dismiss any cookie consent dialog if it appears
#     try:
#         cookie_button = WebDriverWait(driver, 5).until(
#             EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept all') or contains(., 'I agree')]"))
#         )
#         cookie_button.click()
#         print("✅ Dismissed cookie consent")
#         time.sleep(2)
#     except:
#         pass  # If no cookie dialog, continue

#     # Locate the results container using XPath
#     try:
#         scrollable = WebDriverWait(driver, 15).until(
#             EC.presence_of_element_located((By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]'))
#         )
#     except TimeoutException:
#         print("❌ Could not find the results container.")
#         return results

#     # Keep scrolling until no more new results
#     while stagnant_scrolls < max_stagnant_scrolls:
#         wait_for_loading_to_finish()
        
#         # Random delay between actions to appear more human
#         time.sleep(random.uniform(1.5, 3.5))
        
#         listings = driver.find_elements(By.CLASS_NAME, "Nv2PK")  # Each business card

#         # Loop through NEW listings only
#         for listing in listings[len(results):]:
#             try:
#                 name = listing.find_element(By.CLASS_NAME, "qBF1Pd").text
#             except NoSuchElementException:
#                 name = ""

#             try:
#                 rating = listing.find_element(By.CLASS_NAME, "MW4etd").text
#             except NoSuchElementException:
#                 rating = ""

#             try:
#                 details = listing.find_elements(By.CLASS_NAME, "W4Efsd")
#                 category = details[0].text if len(details) > 0 else ""
#                 address = details[1].text if len(details) > 1 else ""
#             except:
#                 category, address = "", ""

#             record = {
#                 "Name": name,
#                 "Category": category,
#                 "Rating": rating,
#                 "Address": address
#             }

#             results.append(record)
#             save_to_csv(record, RAW_FILE)
#             print(f"✅ Saved: {record['Name']}")

#         # Stop if no new results
#         if len(listings) == prev_len:
#             stagnant_scrolls += 1
#             print(f"⏳ No new results ({stagnant_scrolls}/{max_stagnant_scrolls})")
#         else:
#             stagnant_scrolls = 0
#         prev_len = len(listings)

#         # Scroll using human-like behavior
#         human_like_scroll(scrollable, driver)
        
#         # Occasionally scroll back up a little to mimic human behavior
#         if random.random() < 0.2:  # 20% chance
#             current_pos = driver.execute_script("return arguments[0].scrollTop", scrollable)
#             scroll_back = random.randint(50, 200)
#             driver.execute_script("arguments[0].scrollTop = arguments[1]", scrollable, max(0, current_pos - scroll_back))
#             time.sleep(random.uniform(0.5, 1.5))

#     print("✅ No more results to load.")
#     return results

# def remove_duplicates(input_file, output_file):
#     """Remove duplicate rows based on Name + Address"""
#     seen = set()
#     clean_rows = []

#     with open(input_file, mode="r", encoding="utf-8") as infile:
#         reader = csv.DictReader(infile)
#         for row in reader:
#             key = (row["Name"], row["Address"])
#             if key not in seen:
#                 seen.add(key)
#                 clean_rows.append(row)

#     # Write clean file
#     with open(output_file, mode="w", newline="", encoding="utf-8") as outfile:
#         writer = csv.DictWriter(outfile, fieldnames=["Name", "Category", "Rating", "Address"])
#         writer.writeheader()
#         writer.writerows(clean_rows)

#     print(f"\n✨ Cleaned data saved: {len(clean_rows)} unique results")

# if __name__ == "__main__":
#     keywords = [
#         "real estate in miami Florida",
#         "real estate agent in miami Florida",
#         "estate agent in miami Florida",
#         "estate in miami Florida",
#         "agent in miami Florida"
#     ]

#     all_results = []
#     for keyword in keywords:
#         results = scrape_google_maps(keyword)
#         all_results.extend(results)
        
#         # Random delay between keywords to avoid being blocked
#         if keyword != keywords[-1]:  # Don't wait after the last keyword
#             delay = random.randint(10, 30)
#             print(f"⏳ Waiting {delay} seconds before next search...")
#             time.sleep(delay)

#     driver.quit()

#     # Remove duplicates after scraping
#     remove_duplicates(RAW_FILE, CLEAN_FILE)




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
RAW_FILE = "google_maps_raw.csv"
CLEAN_FILE = "google_maps_clean.csv"

# Create RAW CSV with headers (overwrite if exists)
with open(RAW_FILE, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Name", "Rating", "ReviewCount", "Category", "Address", "Hours", "Phone"])


def save_to_csv(record, filename):
    """Save record to CSV file"""
    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            record["Name"],
            record["Rating"],
            record["ReviewCount"],
            record["Category"],
            record["Address"],
            record["Hours"],
            record["Phone"]
        ])


def wait_for_loading_to_finish():
    """Wait for Google Maps 'loading' spinner to disappear"""
    try:
        WebDriverWait(driver, 10).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.m6QErb.DxyBCb.kA9KIf.dS8AEf[aria-busy='true']"))
        )
    except TimeoutException:
        pass


def visible_scroll(scrollable_element, driver):
    """Scroll visibly through the Google Maps results"""
    listings = driver.find_elements(By.CLASS_NAME, "Nv2PK")
    if listings:
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", listings[-1])
        time.sleep(random.uniform(2, 4))


def scrape_google_maps(keyword):
    """Scrape ALL Google Maps results for a given keyword"""
    print(f"\n🔍 Scraping: {keyword}")
    url = f"https://www.google.com/maps/search/{keyword.replace(' ', '+')}"
    driver.get(url)
    time.sleep(5)

    results = []
    prev_len = 0
    stagnant_scrolls = 0
    max_stagnant_scrolls = 5

    # Dismiss cookie consent if it appears
    try:
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept all') or contains(., 'I agree')]"))
        )
        cookie_button.click()
        print("✅ Dismissed cookie consent")
        time.sleep(2)
    except:
        pass

    # Locate the results container
    try:
        scrollable = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]'))
        )
    except TimeoutException:
        print("❌ Could not find the results container.")
        return results

    # Keep scrolling until no more results
    while stagnant_scrolls < max_stagnant_scrolls:
        wait_for_loading_to_finish()
        time.sleep(random.uniform(1.5, 3.5))

        listings = driver.find_elements(By.CLASS_NAME, "Nv2PK")

        # Loop through NEW listings only
        for listing in listings[len(results):]:
            # Default values
            name, rating, review_count, category, address, hours, phone = "", "", "", "", "", "", ""

            try:
                name = listing.find_element(By.CLASS_NAME, "qBF1Pd").text
            except NoSuchElementException:
                pass

            try:
                rating_text = listing.find_element(By.CLASS_NAME, "MW4etd").text
                if "(" in rating_text:
                    rating, review_count = rating_text.split("(", 1)
                    rating = rating.strip()
                    review_count = review_count.replace(")", "").strip()
                else:
                    rating = rating_text
            except NoSuchElementException:
                pass

            try:
                details = listing.find_elements(By.CLASS_NAME, "W4Efsd")
                if len(details) > 0:
                    category = details[0].text
                if len(details) > 1:
                    address = details[1].text
            except:
                pass

            try:
                hours = listing.find_element(By.CLASS_NAME, "o0Svhf").text
            except NoSuchElementException:
                pass

            try:
                phone = listing.find_element(By.CLASS_NAME, "UsdlK").text
            except NoSuchElementException:
                pass

            record = {
                "Name": name,
                "Rating": rating,
                "ReviewCount": review_count,
                "Category": category,
                "Address": address,
                "Hours": hours,
                "Phone": phone
            }

            results.append(record)
            save_to_csv(record, RAW_FILE)
            print(f"✅ Saved: {record['Name']}")

        # Stop if no new results
        if len(listings) == prev_len:
            stagnant_scrolls += 1
            print(f"⏳ No new results ({stagnant_scrolls}/{max_stagnant_scrolls})")
        else:
            stagnant_scrolls = 0
        prev_len = len(listings)

        visible_scroll(scrollable, driver)

    print("✅ No more results to load.")
    return results


def remove_duplicates(input_file, output_file):
    """Remove duplicate rows based on Name + Address + Phone"""
    seen = set()
    clean_rows = []

    with open(input_file, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            key = (row["Name"], row["Address"], row["Phone"])
            if key not in seen:
                seen.add(key)
                clean_rows.append(row)

    with open(output_file, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["Name", "Rating", "ReviewCount", "Category", "Address", "Hours", "Phone"])
        writer.writeheader()
        writer.writerows(clean_rows)

    print(f"\n✨ Cleaned data saved: {len(clean_rows)} unique results")


if __name__ == "__main__":
    keywords = [
        "real estate in miami Florida",
        "real estate agent in miami Florida",
        "estate agent in miami Florida",
        "estate in miami Florida",
        "agent in miami Florida"
    ]

    all_results = []
    for keyword in keywords:
        results = scrape_google_maps(keyword)
        all_results.extend(results)

        if keyword != keywords[-1]:
            delay = random.randint(10, 20)
            print(f"⏳ Waiting {delay} seconds before next search...")
            time.sleep(delay)

    driver.quit()

    # Deduplicate results
    remove_duplicates(RAW_FILE, CLEAN_FILE)
