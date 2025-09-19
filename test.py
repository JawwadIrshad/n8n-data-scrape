import pandas as pd
import re
import csv

# Load your CSV, force all data to string
df = pd.read_csv("google_maps_clean.csv", dtype=str)

cleaned_rows = []

# Regex to detect phone numbers
phone_pattern = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')

# Optional: regex to remove symbols/icons like ''
symbol_pattern = re.compile(r'[^\w\s\d.,:-/]')  # removes non-alphanumeric except common punctuation

for _, row in df.iterrows():
    name = str(row.get('Name', '') or '').strip()
    rating_review = str(row.get('Rating+Review', '') or '').strip()  # Adjust column name if different
    avg_rating = str(row.get('AverageRating', '') or '').strip()      # Adjust column name if different
    full_details = str(row.get('FullDetails', '') or '').strip()      # Column with "Real estate agency ·  · 90 SW 3rd St CU3 Open ⋅ Closes 6:30 pm · +1 305-728-0840"

    # Remove unwanted symbols/icons
    full_details_clean = symbol_pattern.sub('', full_details)

    # Split by '·' to get parts
    parts = [p.strip() for p in full_details_clean.split('·') if p.strip()]

    # Initialize fields
    category, address, hours, phone = '', '', '', ''

    if len(parts) >= 1:
        category = parts[0]
    if len(parts) >= 2:
        address = parts[1]
    if len(parts) >= 3:
        hours = parts[2]
    if len(parts) >= 4:
        phone = parts[3]

    # Sometimes phone is missing from parts but exists inside hours
    if not phone:
        phone_match = phone_pattern.search(hours)
        if phone_match:
            phone = phone_match.group()
            hours = hours.replace(phone, '').strip()

    cleaned_rows.append({
        'Name': name,
        'Rating+Review': rating_review,
        'AverageRating': avg_rating,
        'Category': category,
        'Address': address,
        'Hours': hours,
        'Phone': phone
    })

# Convert to DataFrame
df_cleaned = pd.DataFrame(cleaned_rows)

# Save cleaned CSV
df_cleaned.to_csv("google_maps_cleaned_final.csv", index=False, quoting=csv.QUOTE_ALL)

print("✅ Cleaned CSV saved as 'google_maps_cleaned_final.csv'")
