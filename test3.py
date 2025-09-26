# import requests
# import re
# import os
# import csv

# # ==========================
# # CONFIG
# # ==========================
# input_file = "test.csv"   # CSV file containing website URLs
# output_file = "emails.csv"

# # Regex for finding emails
# EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

# # Domains we consider fake/bad
# BAD_DOMAINS = {"test", "invalid", "example", "localhost"}

# # ==========================
# # FUNCTIONS
# # ==========================
# def is_valid_email(email):
#     """Check if email looks valid and not from fake domains"""
#     if "@" not in email:
#         return False
#     domain = email.split("@")[-1].lower()
#     if any(domain.endswith("." + bad) for bad in BAD_DOMAINS):
#         return False
#     return True

# def scrape_emails(url, index):
#     try:
#         response = requests.get(url, timeout=10)
#         response.raise_for_status()
#         html_file = f"site_{index}.html"

#         # Save HTML temporarily
#         with open(html_file, "w", encoding="utf-8") as f:
#             f.write(response.text)

#         # Extract emails
#         raw_emails = re.findall(EMAIL_REGEX, response.text)

#         # Validate and clean emails
#         emails = [e for e in raw_emails if is_valid_email(e)]

#         # Remove duplicates
#         emails = list(set(emails))

#         # Delete HTML file
#         os.remove(html_file)

#         return emails
#     except Exception as e:
#         print(f"❌ Error scraping {url}: {e}")
#         return []

# def read_websites_from_csv(file_path):
#     websites = []
#     with open(file_path, "r", encoding="utf-8") as csvfile:
#         reader = csv.reader(csvfile)
#         for row in reader:
#             if row:  # avoid empty lines
#                 websites.append(row[0].strip())
#     return websites

# # ==========================
# # MAIN SCRIPT
# # ==========================
# if __name__ == "__main__":
#     websites = read_websites_from_csv(input_file)
#     all_results = []

#     for idx, site in enumerate(websites, start=1):
#         print(f"🔎 Scraping {site} ...")
#         found_emails = scrape_emails(site, idx)
#         if found_emails:
#             for email in found_emails:
#                 all_results.append([site, email])
#         else:
#             all_results.append([site, "No valid emails found"])

#     # Save results to CSV
#     with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(["Website", "Email"])
#         writer.writerows(all_results)

#     print(f"\n✅ Scraping finished. Results saved to {output_file}")


# import csv
# import re
# import time
# import random
# import sys
# from urllib.parse import urlparse
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import TimeoutException, WebDriverException
# from selenium.webdriver.chrome.options import Options

# try:
#     from webdriver_manager.chrome import ChromeDriverManager
#     _WM_AVAILABLE = True
# except Exception:
#     _WM_AVAILABLE = False

# try:
#     from bs4 import BeautifulSoup
#     _BS4_AVAILABLE = True
# except Exception:
#     _BS4_AVAILABLE = False

# TEST_CSV = "test.csv"
# RESULTS_CSV = "results.csv"
# UNIQUE_TXT = "unique_emails.txt"

# EMAIL_REGEX = re.compile(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}', re.UNICODE)

# PAGE_LOAD_TIMEOUT = 30
# IMPLICIT_WAIT = 5
# RANDOM_DELAY_MIN = 1.0
# RANDOM_DELAY_MAX = 3.0
# HEADLESS = True


# def make_driver(headless=True):
#     opts = Options()
#     if headless:
#         opts.add_argument("--headless=new")
#     opts.add_argument("--no-sandbox")
#     opts.add_argument("--disable-dev-shm-usage")
#     opts.add_argument("--start-maximized")
#     opts.add_experimental_option("excludeSwitches", ["enable-automation"])
#     opts.add_experimental_option("useAutomationExtension", False)
#     opts.add_argument("--disable-blink-features=AutomationControlled")
#     try:
#         if _WM_AVAILABLE:
#             service = Service(ChromeDriverManager().install())
#         else:
#             service = Service()
#         driver = webdriver.Chrome(service=service, options=opts)
#         driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
#         driver.implicitly_wait(IMPLICIT_WAIT)
#         return driver
#     except WebDriverException as e:
#         print("Failed to start Chrome WebDriver:", e)
#         raise


# def pop_first_url_from_csv(path):
#     """
#     Read CSV and return the first non-empty URL (first non-empty cell in first non-empty row).
#     Then rewrite the CSV without that row (i.e. remove it).
#     Returns: url string or None if no URL found.
#     """
#     try:
#         with open(path, newline='', encoding='utf-8') as f:
#             rows = list(csv.reader(f))
#     except FileNotFoundError:
#         return None

#     # find index of first row that contains a candidate URL
#     first_idx = None
#     first_url = None
#     for i, row in enumerate(rows):
#         if not row:
#             continue
#         # find first non-empty cell
#         for cell in row:
#             if cell and cell.strip():
#                 candidate = cell.strip()
#                 # try to normalize a bit
#                 if "http" in candidate or candidate.count('.') >= 1:
#                     # add scheme if missing
#                     if not urlparse(candidate).scheme:
#                         candidate = "http://" + candidate
#                     first_idx = i
#                     first_url = candidate
#                 else:
#                     # fallback: still treat as raw string -> add http://
#                     if candidate:
#                         if not urlparse(candidate).scheme:
#                             candidate = "http://" + candidate
#                         first_idx = i
#                         first_url = candidate
#                 break
#         if first_idx is not None:
#             break

#     if first_idx is None:
#         return None

#     # remove that row and write remaining back
#     remaining = [r for j, r in enumerate(rows) if j != first_idx]
#     with open(path, "w", newline='', encoding='utf-8') as f:
#         writer = csv.writer(f)
#         writer.writerows(remaining)
#     return first_url


# def extract_emails_from_text(text):
#     return set(m.group(0) for m in EMAIL_REGEX.finditer(text))


# def extract_mailto_links(html):
#     emails = set()
#     if _BS4_AVAILABLE:
#         soup = BeautifulSoup(html, "html.parser")
#         for a in soup.find_all("a", href=True):
#             href = a["href"].strip()
#             if href.lower().startswith("mailto:"):
#                 mail = href[len("mailto:"):].split('?')[0]
#                 if '@' in mail:
#                     emails.add(mail)
#     else:
#         for m in re.finditer(r'href=["\']mailto:([^"\']+)["\']', html, re.IGNORECASE):
#             candidate = m.group(1).split('?')[0]
#             if '@' in candidate:
#                 emails.add(candidate)
#     return emails


# def append_emails_to_csv(source_url, emails):
#     header_needed = False
#     try:
#         with open(RESULTS_CSV, "r", encoding='utf-8', newline='') as f:
#             pass
#     except FileNotFoundError:
#         header_needed = True

#     with open(RESULTS_CSV, "a", encoding='utf-8', newline='') as f:
#         writer = csv.writer(f)
#         if header_needed:
#             writer.writerow(["source_url", "email"])
#         for e in emails:
#             writer.writerow([source_url, e])


# def update_unique_file(all_emails_set):
#     try:
#         with open(UNIQUE_TXT, "w", encoding='utf-8') as f:
#             for e in sorted(all_emails_set):
#                 f.write(e + "\n")
#     except Exception as ex:
#         print("Failed to write unique emails file:", ex)


# def main():
#     driver = make_driver(headless=HEADLESS)
#     total_found = set()

#     while True:
#         url = pop_first_url_from_csv(TEST_CSV)
#         if not url:
#             print("No more URLs in", TEST_CSV, "- exiting.")
#             break

#         print("Processing:", url)
#         html = ""
#         try:
#             driver.get(url)
#             # small random wait to let page scripts run
#             time.sleep(random.uniform(1.0, 2.5))
#             html = driver.page_source or ""
#         except TimeoutException:
#             print("  - Timeout loading", url)
#             html = driver.page_source or ""
#         except Exception as e:
#             print("  - Error loading URL:", e)
#             # proceed with whatever page source we have (maybe empty)

#         # extract
#         emails = set()
#         mailto_emails = extract_mailto_links(html)
#         if mailto_emails:
#             emails.update(mailto_emails)

#         emails_from_html = extract_emails_from_text(html)
#         if emails_from_html:
#             emails.update(emails_from_html)

#         # also try to read anchor text (visible) for obfuscated but simple cases
#         try:
#             anchors = driver.find_elements(By.TAG_NAME, "a")
#             for a in anchors:
#                 try:
#                     txt = a.text or ""
#                     if '@' in txt:
#                         emails.update(extract_emails_from_text(txt))
#                 except Exception:
#                     pass
#         except Exception:
#             pass

#         if emails:
#             print(f"  - Found {len(emails)} email(s): {', '.join(sorted(emails))}")
#             append_emails_to_csv(url, emails)
#             total_found.update(emails)
#             update_unique_file(total_found)
#         else:
#             print("  - No emails found on this page. Still appending nothing and continuing.")

#         # polite delay before next iteration
#         time.sleep(random.uniform(RANDOM_DELAY_MIN, RANDOM_DELAY_MAX))

#     driver.quit()
#     print("Finished. Total unique emails found across run:", len(total_found))


# if __name__ == "__main__":
#     main()


"""
email_scraper_readonly.py

Alternative solution for scraping emails from websites listed in test.csv.

Behavior:
- Reads all URLs from test.csv (does NOT remove them).
- Try fast fetch via requests; extract emails.
- If none found or if JS likely required, render using Playwright and re-check.
- Deobfuscate common email obfuscations.
- Append findings to results.csv and persist unique emails to unique_emails.txt and emails.db (SQLite).
"""

import csv
import re
import time
import random
import sqlite3
import logging
from pathlib import Path
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

# Playwright import (sync API)
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    _PW_AVAILABLE = True
except Exception:
    _PW_AVAILABLE = False

# ---------------- CONFIG ----------------
TEST_CSV = "output.csv"
RESULTS_CSV = "results copy.csv"
UNIQUE_TXT = "unique_emails2.txt"
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

if __name__ == "__main__":
    main()
