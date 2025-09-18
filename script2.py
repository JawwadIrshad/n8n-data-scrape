import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ========================
# CONFIG
# ========================
KEYWORD = "real estate brokers miami Florida"
RAW_CSV = "raw_results.csv"
CLEAN_CSV = "clean_results.csv"

# ========================
# Selenium Setup
# ========================
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=options)

# ========================
# Open Google Maps
# ========================
driver.get("https://www.google.com/maps")

# Wait for search box
search_box = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.ID, "searchboxinput"))
)
search_box.send_keys(KEYWORD)
search_box.send_keys(Keys.ENTER)

# ========================
# Scroll in results panel
# ========================
time.sleep(5)  # wait for results to load
scrollable_div = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="QA0Szd"]/div/div'))
)

prev_height = 0
while True:
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
    time.sleep(3)  # wait for new results to load

    new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
    if new_height == prev_height:  # no more new results
        break
    prev_height = new_height

print("✅ Finished scrolling all results.")

# ========================
# Scrape results
# ========================
results = driver.find_elements(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div')
data = []

for r in results:
    try:
        name = r.find_element(By.TAG_NAME, "h3").text
    except:
        name = ""

    if name:
        data.append([name])

# ========================
# Save raw results
# ========================
with open(RAW_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Name"])
    writer.writerows(data)

# ========================
# Remove duplicates & save clean
# ========================
unique_data = []
seen = set()
for row in data:
    if row[0] not in seen:
        seen.add(row[0])
        unique_data.append(row)

with open(CLEAN_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Name"])
    writer.writerows(unique_data)

print(f"📂 Saved {len(data)} raw results in {RAW_CSV}")
print(f"📂 Saved {len(unique_data)} unique results in {CLEAN_CSV}")

driver.quit()
