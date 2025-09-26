# import pandas as pd
# import re
# import csv

# # Load your CSV, force all data to string
# df = pd.read_csv("google_maps_clean.csv", dtype=str)

# cleaned_rows = []

# # Regex to detect phone numbers
# phone_pattern = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')

# # Optional: regex to remove symbols/icons like ''
# symbol_pattern = re.compile(r'[^\w\s\d.,:-/]')  # removes non-alphanumeric except common punctuation

# for _, row in df.iterrows():
#     name = str(row.get('Name', '') or '').strip()
#     rating_review = str(row.get('Rating+Review', '') or '').strip()  # Adjust column name if different
#     avg_rating = str(row.get('AverageRating', '') or '').strip()      # Adjust column name if different
#     full_details = str(row.get('FullDetails', '') or '').strip()      # Column with "Real estate agency ·  · 90 SW 3rd St CU3 Open ⋅ Closes 6:30 pm · +1 305-728-0840"

#     # Remove unwanted symbols/icons
#     full_details_clean = symbol_pattern.sub('', full_details)

#     # Split by '·' to get parts
#     parts = [p.strip() for p in full_details_clean.split('·') if p.strip()]

#     # Initialize fields
#     category, address, hours, phone = '', '', '', ''

#     if len(parts) >= 1:
#         category = parts[0]
#     if len(parts) >= 2:
#         address = parts[1]
#     if len(parts) >= 3:
#         hours = parts[2]
#     if len(parts) >= 4:
#         phone = parts[3]

#     # Sometimes phone is missing from parts but exists inside hours
#     if not phone:
#         phone_match = phone_pattern.search(hours)
#         if phone_match:
#             phone = phone_match.group()
#             hours = hours.replace(phone, '').strip()

#     cleaned_rows.append({
#         'Name': name,
#         'Rating+Review': rating_review,
#         'AverageRating': avg_rating,
#         'Category': category,
#         'Address': address,
#         'Hours': hours,
#         'Phone': phone
#     })

# # Convert to DataFrame
# df_cleaned = pd.DataFrame(cleaned_rows)

# # Save cleaned CSV
# df_cleaned.to_csv("google_maps_cleaned_final.csv", index=False, quoting=csv.QUOTE_ALL)

# print("✅ Cleaned CSV saved as 'google_maps_cleaned_final.csv'")



import csv

# Input and output file paths
input_file = "output.csv"
output_file = "output2.csv"

# Open input CSV and remove duplicates
seen = set()
rows = []
duplicate_count = 0

with open(input_file, "r", newline="", encoding="utf-8") as infile:
    reader = csv.reader(infile)
    header = next(reader)  # Save header
    for row in reader:
        row_tuple = tuple(row)  # Convert to tuple (hashable)
        if row_tuple not in seen:
            seen.add(row_tuple)
            rows.append(row)
        else:
            duplicate_count += 1

# Write unique rows to new CSV
with open(output_file, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.writer(outfile)
    writer.writerow(header)   # Write header
    writer.writerows(rows)

print(f"✅ Duplicates removed: {duplicate_count}")
print(f"📂 Clean file saved as '{output_file}' with {len(rows)} unique rows.")




# #!/usr/bin/env python3
# """
# Simple Google Maps Search and Scroll Script

# This script searches Google Maps for a keyword and scrolls through all results
# to load the complete list of businesses.

# Usage: python simple_maps_scraper.py
# """

# import time
# import random
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException

# # Configuration
# SEARCH_KEYWORD = "restaurants in miami florida"  # Change this to your search term
# MAX_SCROLL_ATTEMPTS = 50
# MAX_NO_NEW_RESULTS = 5

# def setup_driver():
#     """Setup Chrome driver"""
#     options = webdriver.ChromeOptions()
#     options.add_argument("--start-maximized")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
#     driver = webdriver.Chrome(options=options)
#     driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
#     return driver

# def scroll_to_load_all_results(driver):
#     """Scroll through Google Maps results until ALL are loaded"""
#     print("Starting to scroll through results...")
    
#     scroll_attempts = 0
#     consecutive_no_new = 0
#     previous_count = 0
#     max_consecutive_no_new = 8
    
#     # Correct XPath for Google Maps scroll container
#     scroll_container_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]'
    
#     while scroll_attempts < MAX_SCROLL_ATTEMPTS and consecutive_no_new < max_consecutive_no_new:
#         # Get current number of results
#         listings = driver.find_elements(By.CLASS_NAME, "Nv2PK")
#         current_count = len(listings)
        
#         # Multiple scrolling strategies using the correct XPath
#         scrolled_successfully = False
        
#         try:
#             # Strategy 1: Use the specific scroll container XPath
#             scrollable = driver.find_element(By.XPATH, scroll_container_xpath)
            
#             # Get current scroll position
#             current_scroll_pos = driver.execute_script("return arguments[0].scrollTop", scrollable)
            
#             # Scroll to bottom of container
#             driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable)
            
#             # Check if scroll position changed
#             time.sleep(2)
#             new_scroll_pos = driver.execute_script("return arguments[0].scrollTop", scrollable)
            
#             if abs(new_scroll_pos - current_scroll_pos) > 50:
#                 scrolled_successfully = True
            
#         except Exception as e:
#             print(f"Primary scroll method failed: {e}")
        
#         # If primary method didn't work well, try alternatives
#         if not scrolled_successfully:
#             try:
#                 # Strategy 2: Try the broader container
#                 fallback_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]'
#                 scrollable = driver.find_element(By.XPATH, fallback_xpath)
#                 driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable)
#                 scrolled_successfully = True
#             except:
#                 # Strategy 3: Scroll to last listing
#                 if listings:
#                     try:
#                         driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", listings[-1])
#                         scrolled_successfully = True
#                     except:
#                         pass
        
#         # If still not scrolled, try incremental scrolls
#         if not scrolled_successfully:
#             try:
#                 scrollable = driver.find_element(By.XPATH, scroll_container_xpath)
#                 for _ in range(5):
#                     driver.execute_script("arguments[0].scrollBy(0, 400);", scrollable)
#                     time.sleep(0.5)
#             except:
#                 # Last resort: page scroll
#                 driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
#         # Wait for results to load
#         time.sleep(random.uniform(3, 5))
        
#         # Check if new results were loaded
#         new_listings = driver.find_elements(By.CLASS_NAME, "Nv2PK")
#         new_count = len(new_listings)
        
#         if new_count > previous_count:
#             # New results found
#             newly_loaded = new_count - previous_count
#             consecutive_no_new = 0
#             print(f"Scroll {scroll_attempts + 1}: +{newly_loaded} new results (Total: {new_count})")
#         else:
#             # No new results
#             consecutive_no_new += 1
#             print(f"Scroll {scroll_attempts + 1}: No new results ({consecutive_no_new}/{max_consecutive_no_new})")
            
#             # When stuck, try more aggressive scrolling
#             if consecutive_no_new >= 3 and consecutive_no_new <= 6:
#                 print("Trying more aggressive scrolling...")
#                 try:
#                     scrollable = driver.find_element(By.XPATH, scroll_container_xpath)
#                     # Multiple small scrolls
#                     for i in range(10):
#                         driver.execute_script("arguments[0].scrollBy(0, 300);", scrollable)
#                         time.sleep(0.3)
#                 except Exception as e:
#                     print(f"Aggressive scroll failed: {e}")
        
#         # Enhanced end detection
#         try:
#             end_indicators = [
#                 "You've reached the end of the list",
#                 "No more results",
#                 "That's all we found",
#                 "You've seen all the results",
#                 "No more places to show",
#                 "End of results"
#             ]
            
#             page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
            
#             for indicator in end_indicators:
#                 if indicator.lower() in page_text:
#                     print(f"Found end indicator: '{indicator}' - All results loaded!")
#                     return new_count
                    
#         except Exception as e:
#             pass
        
#         previous_count = new_count
#         scroll_attempts += 1
        
#         # Progress update
#         if scroll_attempts % 5 == 0:
#             print(f"Progress: Attempt {scroll_attempts}/{MAX_SCROLL_ATTEMPTS}, Results: {new_count}, No-new streak: {consecutive_no_new}")
    
#     final_count = len(driver.find_elements(By.CLASS_NAME, "Nv2PK"))
    
#     if consecutive_no_new >= max_consecutive_no_new:
#         print(f"Stopped: No new results for {consecutive_no_new} consecutive attempts")
#     else:
#         print(f"Stopped: Reached maximum scroll attempts ({MAX_SCROLL_ATTEMPTS})")
    
#     print(f"Final result count: {final_count}")
#     return final_count

# def search_and_scroll(keyword):
#     """Main function to search Google Maps and scroll through results"""
#     print(f"Searching Google Maps for: '{keyword}'")
    
#     driver = setup_driver()
    
#     try:
#         # Navigate to Google Maps with search
#         search_url = f"https://www.google.com/maps/search/{keyword.replace(' ', '+')}"
#         driver.get(search_url)
#         print(f"Opened URL: {search_url}")
        
#         # Wait for results to load
#         try:
#             WebDriverWait(driver, 15).until(
#                 EC.presence_of_element_located((By.CLASS_NAME, "Nv2PK"))
#             )
#             print("Initial results loaded successfully")
#         except TimeoutException:
#             print("Error: Could not find Google Maps results")
#             return
        
#         # Initial wait
#         time.sleep(5)
        
#         # Count initial results
#         initial_listings = driver.find_elements(By.CLASS_NAME, "Nv2PK")
#         print(f"Initial results visible: {len(initial_listings)}")
        
#         # Scroll to load all results
#         final_count = scroll_to_load_all_results(driver)
        
#         print(f"Search completed! Found {final_count} total results for '{keyword}'")
        
#         # Keep browser open for a moment to see results
#         print("Keeping browser open for 10 seconds to view results...")
#         time.sleep(10)
        
#     except Exception as e:
#         print(f"Error during scraping: {e}")
        
#     finally:
#         driver.quit()
#         print("Browser closed")

# if __name__ == "__main__":
#     print("=" * 60)
#     print("Simple Google Maps Search and Scroll Script")
#     print("=" * 60)
    
#     # Run the search
#     search_and_scroll(SEARCH_KEYWORD)
    
#     print("\nScript completed!")
#     print(f"Search term used: '{SEARCH_KEYWORD}'")
#     print("To search for something different, change the SEARCH_KEYWORD variable at the top of the script.")