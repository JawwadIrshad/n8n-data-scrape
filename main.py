# import time
# import csv
# import re
# import random
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import NoSuchElementException, TimeoutException
# import sqlite3
# import logging
# from pathlib import Path
# from urllib.parse import urlparse
# import requests
# from bs4 import BeautifulSoup

# # ==========================
# # Selenium Setup
# # ==========================
# options = webdriver.ChromeOptions()
# options.add_argument("--start-maximized")
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
# options.add_experimental_option("useAutomationExtension", False)

# driver = webdriver.Chrome(options=options)
# driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# # ==========================
# # CSV Setup
# # ==========================
# RESULT_FILE = "business_details.csv"
# with open(RESULT_FILE, "w", newline="", encoding="utf-8") as f:
#     writer = csv.writer(f)
#     writer.writerow(["Name", "Address", "Phone", "Website"])

# # Input and output file paths
# input_file = "business_details.csv"
# output_file = "output.csv"

# # For deduplication
# seen = set()
# rows = []
# duplicate_count = 0

# # ==========================
# # Step 1: Scrape business details from Google Maps
# # ==========================
# def scrape_from_google_maps(keyword):
#     print(f"\n🔍 Searching: {keyword}")
#     url = f"https://www.google.com/maps/search/{keyword.replace(' ', '+')}"
#     driver.get(url)
#     time.sleep(5)

#     businesses = []
#     prev_len = 0
#     stagnant_scrolls = 0
#     max_stagnant = 5

#     try:
#         WebDriverWait(driver, 15).until(
#             EC.presence_of_element_located((By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]'))
#         )
#     except TimeoutException:
#         print("❌ Could not find results container.")
#         return businesses

#     while stagnant_scrolls < max_stagnant:
#         listings = driver.find_elements(By.CLASS_NAME, "Nv2PK")

#         for listing in listings[len(businesses):]:
#             try:
#                 listing.click()
#                 time.sleep(3)

#                 # Name
#                 try:
#                     name = driver.find_element(By.CLASS_NAME, "DUwDvf").text.strip()
#                 except NoSuchElementException:
#                     name = ""

#                 # Address
#                 try:
#                     address = driver.find_element(By.XPATH, '//button[@data-item-id="address"]').text.strip()
#                 except NoSuchElementException:
#                     address = ""

#                 # Phone
#                 phone = ""
#                 phone_raw = ""
#                 try:
#                     phone_raw = driver.find_element(By.XPATH, '//button[@data-item-id="phone"]').text.strip()
#                 except NoSuchElementException:
#                     try:
#                         phone_el = driver.find_element(By.XPATH, '//a[starts-with(@href, "tel:")]')
#                         phone_raw = phone_el.get_attribute("href").replace("tel:", "").strip()
#                     except NoSuchElementException:
#                         try:
#                             phone_raw = driver.find_element(By.XPATH, '//span[contains(text(), "+")]').text.strip()
#                         except NoSuchElementException:
#                             try:
#                                 phone_raw = driver.find_element(By.XPATH, '//span[contains(text(), "(")]').text.strip()
#                             except NoSuchElementException:
#                                 phone_raw = ""

#                 if phone_raw:
#                     phone_digits = re.sub(r"\D", "", phone_raw)
#                     if len(phone_digits) >= 8:
#                         phone = phone_digits
#                     else:
#                         phone = phone_raw

#                 # Website
#                 try:
#                     website_el = driver.find_element(By.XPATH, '//a[@data-item-id="authority"]')
#                     website_url = website_el.get_attribute("href")
#                 except NoSuchElementException:
#                     website_url = ""

#                 if website_url:
#                     businesses.append({
#                         "name": name,
#                         "address": address,
#                         "phone": phone,
#                         "website": website_url
#                     })
#                     print(f"✅ Found: {name} | {website_url} | Phone: {phone}")

#                     with open(RESULT_FILE, "a", newline="", encoding="utf-8") as f:
#                         writer = csv.writer(f)
#                         writer.writerow([name, address, phone, website_url])

#             except Exception:
#                 continue

#         if len(listings) == prev_len:
#             stagnant_scrolls += 1
#         else:
#             stagnant_scrolls = 0
#         prev_len = len(listings)

#         if listings:
#             driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth', block:'end'});", listings[-1])
#             time.sleep(random.uniform(2, 4))

#     print(f"✅ Total businesses with websites: {len(businesses)}")
#     return businesses


# # Playwright import (sync API)
# try:
#     from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
#     _PW_AVAILABLE = True
# except Exception:
#     _PW_AVAILABLE = False

# # ---------------- CONFIG ----------------
# TEST_CSV = "business_details.csv"
# RESULTS_CSV = "results copy.csv"
# UNIQUE_TXT = "unique_emails3.txt"
# DB_FILE = "emails.db"
# LOG_FILE = "scraper.log"

# USE_PLAYWRIGHT = True and _PW_AVAILABLE  # set False to skip headless browser step
# HEADLESS = True
# REQUEST_TIMEOUT = 20  # seconds
# PAGE_TIMEOUT = 30 * 1000  # Playwright timeout in ms

# # Politeness
# MIN_DELAY = 1.0
# MAX_DELAY = 3.0

# # Optional proxy (format: "http://user:pass@host:port" or None)
# PROXY = None

# # Some rotating user agents (simple)
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16 Safari/605.1.15",
#     "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:115.0) Gecko/20100101 Firefox/115.0",
# ]
# # ----------------------------------------

# EMAIL_REGEX = re.compile(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}', re.IGNORECASE)

# OBFUSCATION_PATTERNS = [
#     (re.compile(r'\s*\(\s*at\s*\)\s*', re.IGNORECASE), '@'),
#     (re.compile(r'\s*\[\s*at\s*\]\s*', re.IGNORECASE), '@'),
#     (re.compile(r'\s+at\s+', re.IGNORECASE), '@'),
#     (re.compile(r'\s*\(\s*dot\s*\)\s*', re.IGNORECASE), '.'),
#     (re.compile(r'\s*\[\s*dot\s*\]\s*', re.IGNORECASE), '.'),
#     (re.compile(r'\s+dot\s+', re.IGNORECASE), '.'),
#     (re.compile(r'\s*\{\s*at\s*\}\s*', re.IGNORECASE), '@'),
#     (re.compile(r'\s*\\?/?\s*at\s*\s*', re.IGNORECASE), '@'),
# ]

# logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
#                     format='%(asctime)s [%(levelname)s] %(message)s')
# logger = logging.getLogger(__name__)

# Path(RESULTS_CSV).touch(exist_ok=True)
# Path(UNIQUE_TXT).touch(exist_ok=True)
# Path(DB_FILE).touch(exist_ok=True)

# # ---------- Utility functions ----------

# def read_urls_from_csv(path):
#     """Read all URLs from columns named 'Website' (case-insensitive)."""
#     urls = []
#     try:
#         with open(path, newline='', encoding='utf-8') as f:
#             reader = csv.DictReader(f)
#             if not reader.fieldnames:
#                 return urls

#             # find all columns that contain 'website' in their header
#             website_cols = [col for col in reader.fieldnames if "website" in col.lower()]
#             if not website_cols:
#                 logger.warning("No 'Website' columns found in %s", path)
#                 return urls

#             for row in reader:
#                 for col in website_cols:
#                     candidate = (row.get(col) or "").strip()
#                     if candidate:
#                         if not urlparse(candidate).scheme:
#                             candidate = "http://" + candidate
#                         urls.append(candidate)
#     except FileNotFoundError:
#         logger.error("CSV file not found: %s", path)
#     return urls


# def append_results_csv(source_url, emails):
#     header_needed = not Path(RESULTS_CSV).exists() or Path(RESULTS_CSV).stat().st_size == 0
#     with open(RESULTS_CSV, "a", newline='', encoding='utf-8') as f:
#         writer = csv.writer(f)
#         if header_needed:
#             writer.writerow(["source_url", "email"])
#         for e in sorted(emails):
#             writer.writerow([source_url, e])

# def update_unique_and_txt(all_emails):
#     with open(UNIQUE_TXT, "w", encoding='utf-8') as f:
#         for e in sorted(all_emails):
#             f.write(e + "\n")

# def init_db():
#     conn = sqlite3.connect(DB_FILE)
#     c = conn.cursor()
#     c.execute("""
#     CREATE TABLE IF NOT EXISTS emails (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         source_url TEXT,
#         email TEXT,
#         first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         UNIQUE(source_url, email)
#     )
#     """)
#     conn.commit()
#     return conn

# def save_to_db(conn, source_url, emails):
#     c = conn.cursor()
#     for e in emails:
#         try:
#             c.execute("INSERT OR IGNORE INTO emails (source_url, email) VALUES (?, ?)", (source_url, e))
#         except Exception as ex:
#             logger.warning("DB insert fail for %s -> %s: %s", source_url, e, ex)
#     conn.commit()

# # ---------- Extraction logic ----------

# def find_emails_in_text(text):
#     return set(m.group(0).strip() for m in EMAIL_REGEX.finditer(text))

# def deobfuscate_text(text):
#     s = text
#     for patt, repl in OBFUSCATION_PATTERNS:
#         s = patt.sub(repl, s)
#     return s

# def extract_mailto(html):
#     emails = set()
#     soup = BeautifulSoup(html, "html.parser")
#     for a in soup.select("a[href^=mailto]"):
#         href = a.get("href", "")
#         if href:
#             mail = href.split(":", 1)[1].split("?")[0]
#             if '@' in mail:
#                 emails.add(mail.strip())
#     return emails

# def append_emails_to_csv(csv_path, url, emails):
#     """Append emails into the 'Emails' column of the same row matching the Website URL."""
#     if not emails:
#         return

#     rows = []
#     updated = False

#     with open(csv_path, newline='', encoding='utf-8') as f:
#         reader = csv.DictReader(f)
#         fieldnames = list(reader.fieldnames)

#         # Ensure "Emails" column exists
#         if "Emails" not in fieldnames:
#             fieldnames.append("Emails")

#         for row in reader:
#             row_urls = [row.get(col, "").strip() for col in fieldnames if "website" in col.lower()]
#             if any(u and (u == url or u == url.replace("http://", "").replace("https://", "")) for u in row_urls):
#                 # append emails (unique) to existing column
#                 existing = set((row.get("Emails") or "").split(","))
#                 existing.update(emails)
#                 row["Emails"] = ",".join(sorted(e for e in existing if e))
#                 updated = True
#             rows.append(row)

#     if updated:
#         with open(csv_path, "w", newline='', encoding='utf-8') as f:
#             writer = csv.DictWriter(f, fieldnames=fieldnames)
#             writer.writeheader()
#             writer.writerows(rows)

# def extract_from_html_and_text(html):
#     emails = set()
#     emails.update(find_emails_in_text(html))
#     emails.update(extract_mailto(html))

#     soup = BeautifulSoup(html, "html.parser")
#     for script in soup(["script", "style", "noscript"]):
#         script.extract()
#     visible = soup.get_text(separator=" ")
#     deob = deobfuscate_text(visible)
#     emails.update(find_emails_in_text(deob))

#     for a in soup.find_all("a"):
#         text = (a.get_text() or "").strip()
#         if text:
#             deob_text = deobfuscate_text(text)
#             emails.update(find_emails_in_text(deob_text))
#     return set(e for e in emails if '@' in e)

# # ---------- Fetchers ----------

# def fetch_with_requests(url):
#     headers = {"User-Agent": random.choice(USER_AGENTS)}
#     proxies = {"http": PROXY, "https": PROXY} if PROXY else None
#     try:
#         resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, proxies=proxies)
#         resp.raise_for_status()
#         return resp.text
#     except Exception as ex:
#         logger.info("Requests fetch failed for %s: %s", url, ex)
#         return None

# def fetch_with_playwright(url, playwright):
#     browser = None
#     try:
#         browser = playwright.chromium.launch(headless=HEADLESS)
#         context = browser.new_context(user_agent=random.choice(USER_AGENTS))
#         page = context.new_page()
#         page.goto(url, timeout=PAGE_TIMEOUT)
#         time.sleep(random.uniform(0.5, 1.5))
#         content = page.content()
#         page.close()
#         context.close()
#         browser.close()
#         return content
#     except Exception as ex:
#         logger.warning("Playwright fetch error for %s: %s", url, ex)
#         if browser:
#             try:
#                 browser.close()
#             except Exception:
#                 pass
#         return None

# # ---------- Main loop ----------

# def main():
#     logger.info("Starting scraper")
#     conn = init_db()
#     all_emails = set()
#     try:
#         with open(UNIQUE_TXT, "r", encoding='utf-8') as f:
#             for line in f:
#                 if line.strip():
#                     all_emails.add(line.strip())
#     except Exception:
#         pass

#     pw = None
#     if USE_PLAYWRIGHT and _PW_AVAILABLE:
#         pw = sync_playwright().start()

#     try:
#         urls = read_urls_from_csv(TEST_CSV)
#         for url in urls:
#             logger.info("Processing %s", url)
#             found = set()

#             page_html = fetch_with_requests(url)
#             if page_html:
#                 found = extract_from_html_and_text(page_html)

#             if not found and pw:
#                 logger.info("Trying Playwright for %s", url)
#                 page_html = fetch_with_playwright(url, pw)
#                 if page_html:
#                     found = extract_from_html_and_text(page_html)

#             if found:
#                 normalized = set(e.strip().strip('.,;:()[]<>') for e in found)
#                 append_results_csv(url, normalized)
#                 append_emails_to_csv(TEST_CSV, url, normalized)
#                 save_to_db(conn, url, normalized)
#                 all_emails.update(normalized)
#                 update_unique_and_txt(all_emails)
#                 logger.info("Saved %d emails for %s", len(normalized), url)
#                 print(f"[OK] {url} -> {len(normalized)} emails")
#             else:
#                 logger.info("No emails found for %s", url)
#                 print(f"[NO EMAILS] {url}")

#             time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

#     finally:
#         if pw:
#             try:
#                 pw.stop()
#             except Exception:
#                 pass
#         conn.close()
#         logger.info("Scraper finished")




# def deduplicate_csv():
#     global duplicate_count, rows, seen
#     with open(input_file, "r", newline="", encoding="utf-8") as infile:
#         reader = csv.reader(infile)
#         header = next(reader)
#         for row in reader:
#             row_tuple = tuple(row)
#             if row_tuple not in seen:
#                 seen.add(row_tuple)
#                 rows.append(row)
#             else:
#                 duplicate_count += 1

#     with open(output_file, "w", newline="", encoding="utf-8") as outfile:
#         writer = csv.writer(outfile)
#         writer.writerow(header)
#         writer.writerows(rows)

#     print(f"✅ Duplicates removed: {duplicate_count}")
#     print(f"📂 Clean file saved as '{output_file}' with {len(rows)} unique rows.")


# # ==========================
# # MAIN PIPELINE
# # ==========================
# if __name__ == "__main__":
#     keywords = [
#         "real estate agent in miami Florida",
#         "estate agent in miami Florida"
#     ]

#     # Step 1: Scrape Google Maps
#     for keyword in keywords:
#         scrape_from_google_maps(keyword)
#         time.sleep(random.randint(5, 10))

#     driver.quit()

#     # Step 2: Email scraper
#     main()

#     # Step 3: Deduplicate final CSV
#     deduplicate_csv()

#     print("\n🎯 Scraping complete!")



# # #!/usr/bin/env python3
# # """
# # Google Maps Scraper + Email Scraper + Deduplication
# # - Scrolls through ALL results on Google Maps for given keywords
# # - Extracts business details (Name, Address, Phone, Website)
# # - Fetches emails from the websites found
# # - Saves everything into CSV + SQLite
# # """

# # import time
# # import csv
# # import re
# # import random
# # import sqlite3
# # import logging
# # from pathlib import Path
# # from urllib.parse import urlparse
# # import requests
# # from bs4 import BeautifulSoup
# # from selenium import webdriver
# # from selenium.webdriver.common.by import By
# # from selenium.webdriver.support.ui import WebDriverWait
# # from selenium.webdriver.support import expected_conditions as EC
# # from selenium.common.exceptions import NoSuchElementException, TimeoutException

# # # ==========================
# # # Config
# # # ==========================
# # RESULT_FILE = "business_details.csv"
# # input_file = RESULT_FILE
# # output_file = "output.csv"

# # # For deduplication
# # seen = set()
# # rows = []
# # duplicate_count = 0

# # # ==========================
# # # Selenium Setup
# # # ==========================
# # def setup_driver():
# #     options = webdriver.ChromeOptions()
# #     options.add_argument("--start-maximized")
# #     options.add_argument("--disable-blink-features=AutomationControlled")
# #     options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
# #     options.add_experimental_option("useAutomationExtension", False)

# #     driver = webdriver.Chrome(options=options)
# #     driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
# #     return driver


# # # ==========================
# # # Scrolling Function (from second script)
# # # ==========================
# # def scroll_to_load_all_results(driver, max_scroll_attempts=50, max_no_new=8):
# #     """Scroll through Google Maps results until ALL are loaded"""
# #     print("Starting to scroll through results...")

# #     scroll_attempts = 0
# #     consecutive_no_new = 0
# #     previous_count = 0

# #     scroll_container_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]'

# #     while scroll_attempts < max_scroll_attempts and consecutive_no_new < max_no_new:
# #         listings = driver.find_elements(By.CLASS_NAME, "Nv2PK")
# #         current_count = len(listings)

# #         scrolled_successfully = False
# #         try:
# #             scrollable = driver.find_element(By.XPATH, scroll_container_xpath)
# #             driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable)
# #             time.sleep(2)
# #             scrolled_successfully = True
# #         except:
# #             if listings:
# #                 try:
# #                     driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth', block:'end'});", listings[-1])
# #                     scrolled_successfully = True
# #                 except:
# #                     pass

# #         if not scrolled_successfully:
# #             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# #         time.sleep(random.uniform(2, 4))

# #         new_count = len(driver.find_elements(By.CLASS_NAME, "Nv2PK"))
# #         if new_count > previous_count:
# #             newly_loaded = new_count - previous_count
# #             consecutive_no_new = 0
# #             print(f"Scroll {scroll_attempts+1}: +{newly_loaded} new results (Total: {new_count})")
# #         else:
# #             consecutive_no_new += 1
# #             print(f"Scroll {scroll_attempts+1}: No new results ({consecutive_no_new}/{max_no_new})")

# #         previous_count = new_count
# #         scroll_attempts += 1

# #     return len(driver.find_elements(By.CLASS_NAME, "Nv2PK"))

# # # ==========================
# # # Step 1: Scrape business details from Google Maps
# # # ==========================
# # def scrape_from_google_maps(driver, keyword):
# #     print(f"\n🔍 Searching: {keyword}")
# #     url = f"https://www.google.com/maps/search/{keyword.replace(' ', '+')}"
# #     driver.get(url)

# #     try:
# #         WebDriverWait(driver, 15).until(
# #             EC.presence_of_element_located((By.CLASS_NAME, "Nv2PK"))
# #         )
# #     except TimeoutException:
# #         print("❌ Could not find results container.")
# #         return []

# #     # Scroll all results first
# #     total = scroll_to_load_all_results(driver)
# #     print(f"✅ Total listings loaded: {total}")

# #     businesses = []

# #     listings = driver.find_elements(By.CLASS_NAME, "Nv2PK")
# #     for listing in listings:
# #         try:
# #             driver.execute_script("arguments[0].click();", listing)
# #             time.sleep(3)

# #             try:
# #                 name = driver.find_element(By.CLASS_NAME, "DUwDvf").text.strip()
# #             except NoSuchElementException:
# #                 name = ""

# #             try:
# #                 address = driver.find_element(By.XPATH, '//button[@data-item-id="address"]').text.strip()
# #             except NoSuchElementException:
# #                 address = ""

# #             phone = ""
# #             try:
# #                 phone_raw = driver.find_element(By.XPATH, '//button[@data-item-id="phone"]').text.strip()
# #             except NoSuchElementException:
# #                 phone_raw = ""
# #             if phone_raw:
# #                 phone_digits = re.sub(r"\D", "", phone_raw)
# #                 phone = phone_digits if len(phone_digits) >= 8 else phone_raw

# #             try:
# #                 website_el = driver.find_element(By.XPATH, '//a[@data-item-id="authority"]')
# #                 website_url = website_el.get_attribute("href")
# #             except NoSuchElementException:
# #                 website_url = ""

# #             businesses.append({
# #                 "name": name,
# #                 "address": address,
# #                 "phone": phone,
# #                 "website": website_url
# #             })

# #             with open(RESULT_FILE, "a", newline="", encoding="utf-8") as f:
# #                 writer = csv.writer(f)
# #                 writer.writerow([name, address, phone, website_url])

# #             print(f"✅ Found: {name} | {website_url} | Phone: {phone}")

# #         except Exception:
# #             continue

# #     return businesses


# # # Playwright import (sync API)
# # try:
# #     from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
# #     _PW_AVAILABLE = True
# # except Exception:
# #     _PW_AVAILABLE = False

# # # ---------------- CONFIG ----------------
# # TEST_CSV = "business_details.csv"
# # RESULTS_CSV = "results copy.csv"
# # UNIQUE_TXT = "unique_emails3.txt"
# # DB_FILE = "emails.db"
# # LOG_FILE = "scraper.log"

# # USE_PLAYWRIGHT = True and _PW_AVAILABLE  # set False to skip headless browser step
# # HEADLESS = True
# # REQUEST_TIMEOUT = 20  # seconds
# # PAGE_TIMEOUT = 30 * 1000  # Playwright timeout in ms

# # # Politeness
# # MIN_DELAY = 1.0
# # MAX_DELAY = 3.0

# # # Optional proxy (format: "http://user:pass@host:port" or None)
# # PROXY = None

# # # Some rotating user agents (simple)
# # USER_AGENTS = [
# #     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
# #     "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16 Safari/605.1.15",
# #     "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:115.0) Gecko/20100101 Firefox/115.0",
# # ]
# # # ----------------------------------------

# # EMAIL_REGEX = re.compile(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}', re.IGNORECASE)

# # OBFUSCATION_PATTERNS = [
# #     (re.compile(r'\s*\(\s*at\s*\)\s*', re.IGNORECASE), '@'),
# #     (re.compile(r'\s*\[\s*at\s*\]\s*', re.IGNORECASE), '@'),
# #     (re.compile(r'\s+at\s+', re.IGNORECASE), '@'),
# #     (re.compile(r'\s*\(\s*dot\s*\)\s*', re.IGNORECASE), '.'),
# #     (re.compile(r'\s*\[\s*dot\s*\]\s*', re.IGNORECASE), '.'),
# #     (re.compile(r'\s+dot\s+', re.IGNORECASE), '.'),
# #     (re.compile(r'\s*\{\s*at\s*\}\s*', re.IGNORECASE), '@'),
# #     (re.compile(r'\s*\\?/?\s*at\s*\s*', re.IGNORECASE), '@'),
# # ]

# # logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
# #                     format='%(asctime)s [%(levelname)s] %(message)s')
# # logger = logging.getLogger(__name__)

# # Path(RESULTS_CSV).touch(exist_ok=True)
# # Path(UNIQUE_TXT).touch(exist_ok=True)
# # Path(DB_FILE).touch(exist_ok=True)

# # # ---------- Utility functions ----------

# # def read_urls_from_csv(path):
# #     """Read all URLs from columns named 'Website' (case-insensitive)."""
# #     urls = []
# #     try:
# #         with open(path, newline='', encoding='utf-8') as f:
# #             reader = csv.DictReader(f)
# #             if not reader.fieldnames:
# #                 return urls

# #             # find all columns that contain 'website' in their header
# #             website_cols = [col for col in reader.fieldnames if "website" in col.lower()]
# #             if not website_cols:
# #                 logger.warning("No 'Website' columns found in %s", path)
# #                 return urls

# #             for row in reader:
# #                 for col in website_cols:
# #                     candidate = (row.get(col) or "").strip()
# #                     if candidate:
# #                         if not urlparse(candidate).scheme:
# #                             candidate = "http://" + candidate
# #                         urls.append(candidate)
# #     except FileNotFoundError:
# #         logger.error("CSV file not found: %s", path)
# #     return urls


# # def append_results_csv(source_url, emails):
# #     header_needed = not Path(RESULTS_CSV).exists() or Path(RESULTS_CSV).stat().st_size == 0
# #     with open(RESULTS_CSV, "a", newline='', encoding='utf-8') as f:
# #         writer = csv.writer(f)
# #         if header_needed:
# #             writer.writerow(["source_url", "email"])
# #         for e in sorted(emails):
# #             writer.writerow([source_url, e])

# # def update_unique_and_txt(all_emails):
# #     with open(UNIQUE_TXT, "w", encoding='utf-8') as f:
# #         for e in sorted(all_emails):
# #             f.write(e + "\n")

# # def init_db():
# #     conn = sqlite3.connect(DB_FILE)
# #     c = conn.cursor()
# #     c.execute("""
# #     CREATE TABLE IF NOT EXISTS emails (
# #         id INTEGER PRIMARY KEY AUTOINCREMENT,
# #         source_url TEXT,
# #         email TEXT,
# #         first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
# #         UNIQUE(source_url, email)
# #     )
# #     """)
# #     conn.commit()
# #     return conn

# # def save_to_db(conn, source_url, emails):
# #     c = conn.cursor()
# #     for e in emails:
# #         try:
# #             c.execute("INSERT OR IGNORE INTO emails (source_url, email) VALUES (?, ?)", (source_url, e))
# #         except Exception as ex:
# #             logger.warning("DB insert fail for %s -> %s: %s", source_url, e, ex)
# #     conn.commit()

# # # ---------- Extraction logic ----------

# # def find_emails_in_text(text):
# #     return set(m.group(0).strip() for m in EMAIL_REGEX.finditer(text))

# # def deobfuscate_text(text):
# #     s = text
# #     for patt, repl in OBFUSCATION_PATTERNS:
# #         s = patt.sub(repl, s)
# #     return s

# # def extract_mailto(html):
# #     emails = set()
# #     soup = BeautifulSoup(html, "html.parser")
# #     for a in soup.select("a[href^=mailto]"):
# #         href = a.get("href", "")
# #         if href:
# #             mail = href.split(":", 1)[1].split("?")[0]
# #             if '@' in mail:
# #                 emails.add(mail.strip())
# #     return emails

# # def append_emails_to_csv(csv_path, url, emails):
# #     """Append emails into the 'Emails' column of the same row matching the Website URL."""
# #     if not emails:
# #         return

# #     rows = []
# #     updated = False

# #     with open(csv_path, newline='', encoding='utf-8') as f:
# #         reader = csv.DictReader(f)
# #         fieldnames = list(reader.fieldnames)

# #         # Ensure "Emails" column exists
# #         if "Emails" not in fieldnames:
# #             fieldnames.append("Emails")

# #         for row in reader:
# #             row_urls = [row.get(col, "").strip() for col in fieldnames if "website" in col.lower()]
# #             if any(u and (u == url or u == url.replace("http://", "").replace("https://", "")) for u in row_urls):
# #                 # append emails (unique) to existing column
# #                 existing = set((row.get("Emails") or "").split(","))
# #                 existing.update(emails)
# #                 row["Emails"] = ",".join(sorted(e for e in existing if e))
# #                 updated = True
# #             rows.append(row)

# #     if updated:
# #         with open(csv_path, "w", newline='', encoding='utf-8') as f:
# #             writer = csv.DictWriter(f, fieldnames=fieldnames)
# #             writer.writeheader()
# #             writer.writerows(rows)

# # def extract_from_html_and_text(html):
# #     emails = set()
# #     emails.update(find_emails_in_text(html))
# #     emails.update(extract_mailto(html))

# #     soup = BeautifulSoup(html, "html.parser")
# #     for script in soup(["script", "style", "noscript"]):
# #         script.extract()
# #     visible = soup.get_text(separator=" ")
# #     deob = deobfuscate_text(visible)
# #     emails.update(find_emails_in_text(deob))

# #     for a in soup.find_all("a"):
# #         text = (a.get_text() or "").strip()
# #         if text:
# #             deob_text = deobfuscate_text(text)
# #             emails.update(find_emails_in_text(deob_text))
# #     return set(e for e in emails if '@' in e)

# # # ---------- Fetchers ----------

# # def fetch_with_requests(url):
# #     headers = {"User-Agent": random.choice(USER_AGENTS)}
# #     proxies = {"http": PROXY, "https": PROXY} if PROXY else None
# #     try:
# #         resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, proxies=proxies)
# #         resp.raise_for_status()
# #         return resp.text
# #     except Exception as ex:
# #         logger.info("Requests fetch failed for %s: %s", url, ex)
# #         return None

# # def fetch_with_playwright(url, playwright):
# #     browser = None
# #     try:
# #         browser = playwright.chromium.launch(headless=HEADLESS)
# #         context = browser.new_context(user_agent=random.choice(USER_AGENTS))
# #         page = context.new_page()
# #         page.goto(url, timeout=PAGE_TIMEOUT)
# #         time.sleep(random.uniform(0.5, 1.5))
# #         content = page.content()
# #         page.close()
# #         context.close()
# #         browser.close()
# #         return content
# #     except Exception as ex:
# #         logger.warning("Playwright fetch error for %s: %s", url, ex)
# #         if browser:
# #             try:
# #                 browser.close()
# #             except Exception:
# #                 pass
# #         return None

# # # ---------- Main loop ----------

# # def main():
# #     logger.info("Starting scraper")
# #     conn = init_db()
# #     all_emails = set()
# #     try:
# #         with open(UNIQUE_TXT, "r", encoding='utf-8') as f:
# #             for line in f:
# #                 if line.strip():
# #                     all_emails.add(line.strip())
# #     except Exception:
# #         pass

# #     pw = None
# #     if USE_PLAYWRIGHT and _PW_AVAILABLE:
# #         pw = sync_playwright().start()

# #     try:
# #         urls = read_urls_from_csv(TEST_CSV)
# #         for url in urls:
# #             logger.info("Processing %s", url)
# #             found = set()

# #             page_html = fetch_with_requests(url)
# #             if page_html:
# #                 found = extract_from_html_and_text(page_html)

# #             if not found and pw:
# #                 logger.info("Trying Playwright for %s", url)
# #                 page_html = fetch_with_playwright(url, pw)
# #                 if page_html:
# #                     found = extract_from_html_and_text(page_html)

# #             if found:
# #                 normalized = set(e.strip().strip('.,;:()[]<>') for e in found)
# #                 append_results_csv(url, normalized)
# #                 append_emails_to_csv(TEST_CSV, url, normalized)
# #                 save_to_db(conn, url, normalized)
# #                 all_emails.update(normalized)
# #                 update_unique_and_txt(all_emails)
# #                 logger.info("Saved %d emails for %s", len(normalized), url)
# #                 print(f"[OK] {url} -> {len(normalized)} emails")
# #             else:
# #                 logger.info("No emails found for %s", url)
# #                 print(f"[NO EMAILS] {url}")

# #             time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

# #     finally:
# #         if pw:
# #             try:
# #                 pw.stop()
# #             except Exception:
# #                 pass
# #         conn.close()
# #         logger.info("Scraper finished")




# # def deduplicate_csv():
# #     global duplicate_count, rows, seen
# #     with open(input_file, "r", newline="", encoding="utf-8") as infile:
# #         reader = csv.reader(infile)
# #         header = next(reader)
# #         for row in reader:
# #             row_tuple = tuple(row)
# #             if row_tuple not in seen:
# #                 seen.add(row_tuple)
# #                 rows.append(row)
# #             else:
# #                 duplicate_count += 1

# #     with open(output_file, "w", newline="", encoding="utf-8") as outfile:
# #         writer = csv.writer(outfile)
# #         writer.writerow(header)
# #         writer.writerows(rows)

# #     print(f"✅ Duplicates removed: {duplicate_count}")
# #     print(f"📂 Clean file saved as '{output_file}' with {len(rows)} unique rows.")


# # if __name__ == "__main__":
# #     # prepare CSV header
# #     with open(RESULT_FILE, "w", newline="", encoding="utf-8") as f:
# #         writer = csv.writer(f)
# #         writer.writerow(["Name", "Address", "Phone", "Website"])

# #     keywords = [
# #         "real estate agent in miami Florida",
# #         "estate agent in miami Florida"
# #     ]

# #     driver = setup_driver()

# #     for keyword in keywords:
# #         scrape_from_google_maps(driver, keyword)
# #         time.sleep(random.randint(5, 10))

# #     driver.quit()

# #     # Step 2: Email scraper (call your `main()` here if you want email extraction)

# #     # Step 3: Deduplicate final CSV
# #     deduplicate_csv()

# #     print("\n🎯 Scraping complete!")





import time
import csv
import re
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import sqlite3
import logging
from pathlib import Path
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

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
    writer.writerow(["Name", "Address", "Phone", "Website"])

# Input and output file paths
input_file = "business_details.csv"
output_file = "output.csv"

# For deduplication
seen = set()
rows = []
duplicate_count = 0

# ==========================
# Step 1: Scrape business details from Google Maps
# ==========================
# ==========================
# Selenium Setup
# ==========================
def setup_driver():
    """Setup Chrome driver"""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


def scroll_to_load_all_results(driver):
    """Scroll through Google Maps results until ALL are loaded"""
    print("📜 Scrolling results...")

    scroll_attempts = 0
    consecutive_no_new = 0
    previous_count = 0
    max_consecutive_no_new = 3
    MAX_SCROLL_ATTEMPTS = 50  # you can tune this

    scroll_container_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]'

    while scroll_attempts < MAX_SCROLL_ATTEMPTS and consecutive_no_new < max_consecutive_no_new:
        listings = driver.find_elements(By.CLASS_NAME, "Nv2PK")
        current_count = len(listings)

        try:
            scrollable = driver.find_element(By.XPATH, scroll_container_xpath)
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable)
        except:
            if listings:
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", listings[-1])
            else:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(random.uniform(4, 8))

        new_listings = driver.find_elements(By.CLASS_NAME, "Nv2PK")
        new_count = len(new_listings)

        if new_count > previous_count:
            print(f"Scroll {scroll_attempts+1}: +{new_count-previous_count} new (Total: {new_count})")
            consecutive_no_new = 0
        else:
            consecutive_no_new += 1
            print(f"Scroll {scroll_attempts+1}: No new results ({consecutive_no_new}/{max_consecutive_no_new})")

        previous_count = new_count
        scroll_attempts += 1

    return len(driver.find_elements(By.CLASS_NAME, "Nv2PK"))


def scrape_from_google_maps(keyword, driver):
    """Scroll first, then fetch business details"""
    print(f"\n🔍 Searching: {keyword}")
    url = f"https://www.google.com/maps/search/{keyword.replace(' ', '+')}"
    driver.get(url)

    try:
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Nv2PK"))
        )
    except TimeoutException:
        print("❌ Could not find results container.")
        return []

    # First, scroll through all results
    total = scroll_to_load_all_results(driver)
    print(f"✅ Finished scrolling, found {total} results")

    # Now loop through them and extract details
    businesses = []
    listings = driver.find_elements(By.CLASS_NAME, "Nv2PK")

    for idx, listing in enumerate(listings):
        try:
            driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth', block:'center'});", listing)
            listing.click()
            time.sleep(3)

            # Extract fields (same as before)
            try:
                name = driver.find_element(By.CLASS_NAME, "DUwDvf").text.strip()
            except NoSuchElementException:
                name = ""

            try:
                address = driver.find_element(By.XPATH, '//button[@data-item-id="address"]').text.strip()
            except NoSuchElementException:
                address = ""

            phone = ""
            try:
                phone_raw = driver.find_element(By.XPATH, '//button[@data-item-id="phone"]').text.strip()
                phone = re.sub(r"\D", "", phone_raw) if phone_raw else ""
            except NoSuchElementException:
                pass

            try:
                website_el = driver.find_element(By.XPATH, '//a[@data-item-id="authority"]')
                website_url = website_el.get_attribute("href")
            except NoSuchElementException:
                website_url = ""

            if website_url:
                businesses.append({
                    "name": name,
                    "address": address,
                    "phone": phone,
                    "website": website_url
                })
                print(f"✅ {idx+1}: {name} | {website_url}")

                with open(RESULT_FILE, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([name, address, phone, website_url])

        except Exception:
            continue

    print(f"🎯 Total businesses with websites: {len(businesses)}")
    return businesses



# Playwright import (sync API)
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    _PW_AVAILABLE = True
except Exception:
    _PW_AVAILABLE = False

# ---------------- CONFIG ----------------
TEST_CSV = "output.csv"
RESULTS_CSV = "results copy.csv"
UNIQUE_TXT = "unique_emails3.txt"
DB_FILE = "emails.db"
LOG_FILE = "scraper.log"

USE_PLAYWRIGHT = True and _PW_AVAILABLE  # set False to skip headless browser step
HEADLESS = True
REQUEST_TIMEOUT = 20  # seconds
PAGE_TIMEOUT = 30 * 1000  # Playwright timeout in ms

# Politeness
MIN_DELAY = 1.0
MAX_DELAY = 3.0

# Optional proxy (format: "http://user:pass@host:port" or None)
PROXY = None

# Some rotating user agents (simple)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:115.0) Gecko/20100101 Firefox/115.0",
]
# ----------------------------------------

EMAIL_REGEX = re.compile(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}', re.IGNORECASE)

OBFUSCATION_PATTERNS = [
    (re.compile(r'\s*\(\s*at\s*\)\s*', re.IGNORECASE), '@'),
    (re.compile(r'\s*\[\s*at\s*\]\s*', re.IGNORECASE), '@'),
    (re.compile(r'\s+at\s+', re.IGNORECASE), '@'),
    (re.compile(r'\s*\(\s*dot\s*\)\s*', re.IGNORECASE), '.'),
    (re.compile(r'\s*\[\s*dot\s*\]\s*', re.IGNORECASE), '.'),
    (re.compile(r'\s+dot\s+', re.IGNORECASE), '.'),
    (re.compile(r'\s*\{\s*at\s*\}\s*', re.IGNORECASE), '@'),
    (re.compile(r'\s*\\?/?\s*at\s*\s*', re.IGNORECASE), '@'),
]

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

Path(RESULTS_CSV).touch(exist_ok=True)
Path(UNIQUE_TXT).touch(exist_ok=True)
Path(DB_FILE).touch(exist_ok=True)

# ---------- Utility functions ----------

def read_urls_from_csv(path):
    """Read all URLs from columns named 'Website' (case-insensitive)."""
    urls = []
    try:
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                return urls

            # find all columns that contain 'website' in their header
            website_cols = [col for col in reader.fieldnames if "website" in col.lower()]
            if not website_cols:
                logger.warning("No 'Website' columns found in %s", path)
                return urls

            for row in reader:
                for col in website_cols:
                    candidate = (row.get(col) or "").strip()
                    if candidate:
                        if not urlparse(candidate).scheme:
                            candidate = "http://" + candidate
                        urls.append(candidate)
    except FileNotFoundError:
        logger.error("CSV file not found: %s", path)
    return urls


def append_results_csv(source_url, emails):
    header_needed = not Path(RESULTS_CSV).exists() or Path(RESULTS_CSV).stat().st_size == 0
    with open(RESULTS_CSV, "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if header_needed:
            writer.writerow(["source_url", "email"])
        for e in sorted(emails):
            writer.writerow([source_url, e])

def update_unique_and_txt(all_emails):
    with open(UNIQUE_TXT, "w", encoding='utf-8') as f:
        for e in sorted(all_emails):
            f.write(e + "\n")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_url TEXT,
        email TEXT,
        first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(source_url, email)
    )
    """)
    conn.commit()
    return conn

def save_to_db(conn, source_url, emails):
    c = conn.cursor()
    for e in emails:
        try:
            c.execute("INSERT OR IGNORE INTO emails (source_url, email) VALUES (?, ?)", (source_url, e))
        except Exception as ex:
            logger.warning("DB insert fail for %s -> %s: %s", source_url, e, ex)
    conn.commit()

# ---------- Extraction logic ----------

def find_emails_in_text(text):
    return set(m.group(0).strip() for m in EMAIL_REGEX.finditer(text))

def deobfuscate_text(text):
    s = text
    for patt, repl in OBFUSCATION_PATTERNS:
        s = patt.sub(repl, s)
    return s

def extract_mailto(html):
    emails = set()
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.select("a[href^=mailto]"):
        href = a.get("href", "")
        if href:
            mail = href.split(":", 1)[1].split("?")[0]
            if '@' in mail:
                emails.add(mail.strip())
    return emails

def append_emails_to_csv(csv_path, url, emails):
    """Append emails into the 'Emails' column of the same row matching the Website URL."""
    if not emails:
        return

    rows = []
    updated = False

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)

        # Ensure "Emails" column exists
        if "Emails" not in fieldnames:
            fieldnames.append("Emails")

        for row in reader:
            row_urls = [row.get(col, "").strip() for col in fieldnames if "website" in col.lower()]
            if any(u and (u == url or u == url.replace("http://", "").replace("https://", "")) for u in row_urls):
                # append emails (unique) to existing column
                existing = set((row.get("Emails") or "").split(","))
                existing.update(emails)
                row["Emails"] = ",".join(sorted(e for e in existing if e))
                updated = True
            rows.append(row)

    if updated:
        with open(csv_path, "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

def extract_from_html_and_text(html):
    emails = set()
    emails.update(find_emails_in_text(html))
    emails.update(extract_mailto(html))

    soup = BeautifulSoup(html, "html.parser")
    for script in soup(["script", "style", "noscript"]):
        script.extract()
    visible = soup.get_text(separator=" ")
    deob = deobfuscate_text(visible)
    emails.update(find_emails_in_text(deob))

    for a in soup.find_all("a"):
        text = (a.get_text() or "").strip()
        if text:
            deob_text = deobfuscate_text(text)
            emails.update(find_emails_in_text(deob_text))
    return set(e for e in emails if '@' in e)

# ---------- Fetchers ----------

def fetch_with_requests(url):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    proxies = {"http": PROXY, "https": PROXY} if PROXY else None
    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, proxies=proxies)
        resp.raise_for_status()
        return resp.text
    except Exception as ex:
        logger.info("Requests fetch failed for %s: %s", url, ex)
        return None

def fetch_with_playwright(url, playwright):
    browser = None
    try:
        browser = playwright.chromium.launch(headless=HEADLESS)
        context = browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = context.new_page()
        page.goto(url, timeout=PAGE_TIMEOUT)
        time.sleep(random.uniform(0.5, 1.5))
        content = page.content()
        page.close()
        context.close()
        browser.close()
        return content
    except Exception as ex:
        logger.warning("Playwright fetch error for %s: %s", url, ex)
        if browser:
            try:
                browser.close()
            except Exception:
                pass
        return None

# ---------- Main loop ----------

def main():
    logger.info("Starting scraper")
    conn = init_db()
    all_emails = set()
    try:
        with open(UNIQUE_TXT, "r", encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    all_emails.add(line.strip())
    except Exception:
        pass

    pw = None
    if USE_PLAYWRIGHT and _PW_AVAILABLE:
        pw = sync_playwright().start()

    try:
        urls = read_urls_from_csv(TEST_CSV)
        for url in urls:
            logger.info("Processing %s", url)
            found = set()

            page_html = fetch_with_requests(url)
            if page_html:
                found = extract_from_html_and_text(page_html)

            if not found and pw:
                logger.info("Trying Playwright for %s", url)
                page_html = fetch_with_playwright(url, pw)
                if page_html:
                    found = extract_from_html_and_text(page_html)

            if found:
                normalized = set(e.strip().strip('.,;:()[]<>') for e in found)
                append_results_csv(url, normalized)
                append_emails_to_csv(TEST_CSV, url, normalized)
                save_to_db(conn, url, normalized)
                all_emails.update(normalized)
                update_unique_and_txt(all_emails)
                logger.info("Saved %d emails for %s", len(normalized), url)
                print(f"[OK] {url} -> {len(normalized)} emails")
            else:
                logger.info("No emails found for %s", url)
                print(f"[NO EMAILS] {url}")

            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

    finally:
        if pw:
            try:
                pw.stop()
            except Exception:
                pass
        conn.close()
        logger.info("Scraper finished")




def deduplicate_csv():
    global duplicate_count, rows, seen
    with open(input_file, "r", newline="", encoding="utf-8") as infile:
        reader = csv.reader(infile)
        header = next(reader)
        for row in reader:
            row_tuple = tuple(row)
            if row_tuple not in seen:
                seen.add(row_tuple)
                rows.append(row)
            else:
                duplicate_count += 1

    with open(output_file, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(header)
        writer.writerows(rows)

    print(f"✅ Duplicates removed: {duplicate_count}")
    print(f"📂 Clean file saved as '{output_file}' with {len(rows)} unique rows.")


# ==========================
# MAIN PIPELINE
# ==========================
if __name__ == "__main__":
    driver = setup_driver()
    keywords = [
        "real estate in miami Florida",
        "real estate agent in miami Florida",
        "estate agent in miami Florida",
        "estate in miami Florida",
        "agent in miami Florida",
        "realtor in miami Florida",
        "realty in miami Florida",
        "real estate company in miami Florida",
        "real estate office in miami Florida",
        "real estate agency in miami Florida",
        "real estate broker in miami Florida",
        "real estate services in miami Florida"
    ]

    # Step 1: Scrape Google Maps
    for keyword in keywords:
        scrape_from_google_maps(keyword, driver)
        time.sleep(random.randint(5, 10))

    driver.quit()
    deduplicate_csv()
    # Step 2: Email scraper
    main()

    # Step 3: Deduplicate final CSV
   

    print("\n🎯 Scraping complete!")

