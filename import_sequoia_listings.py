#!/usr/bin/env python3
"""
Import Toyota Sequoia listings from scraped Facebook Marketplace data
"""

import sqlite3
import re
from datetime import datetime
from pathlib import Path

# Sequoia listings data extracted from the RTF file
SEQUOIA_LISTINGS = [
    {"price": 4900, "original_price": 5500, "year": 2004, "model": "sequoia Limited", "location": "Gardnerville, NV", "mileage": 281000, "url": "https://www.facebook.com/marketplace/item/1196591129264299/"},
    {"price": 65446, "year": 2023, "model": "sequoia Capstone Sport Utility 4D", "location": "Folsom, CA", "mileage": 25000, "url": "https://www.facebook.com/marketplace/item/839089815554448/"},
    {"price": 4200, "year": 2005, "model": "sequoia", "location": "Fresno, CA", "mileage": 268000, "url": "https://www.facebook.com/marketplace/item/741317525684841/"},
    {"price": 135, "year": 2005, "model": "sequoia SR5 Sport Utility 4D", "location": "Dinuba, CA", "mileage": 205000, "url": "https://www.facebook.com/marketplace/item/1284212217072116/"},
    {"price": 21000, "year": 2011, "model": "sequoia Limited", "location": "Chico, CA", "mileage": 135000, "url": "https://www.facebook.com/marketplace/item/818402877211860/"},
    {"price": 4450, "original_price": 5000, "year": 2007, "model": "sequoia SR5 Sport Utility 4D", "location": "Fresno, CA", "mileage": 221000, "url": "https://www.facebook.com/marketplace/item/1372946031002079/"},
    {"price": 3900, "original_price": 4500, "year": 2006, "model": "sequoia SR5 Sport Utility 4D", "location": "Madera, CA", "mileage": 300000, "url": "https://www.facebook.com/marketplace/item/1216730943683573/"},
    {"price": 4850, "original_price": 6850, "year": 2002, "model": "sequoia SR5 Sport Utility 4D", "location": "Stevenson Ranch, CA", "mileage": 235000, "url": "https://www.facebook.com/marketplace/item/1212580424229811/"},
    {"price": 120, "year": 2001, "model": "sequoia SR5", "location": "Kerman, CA", "mileage": 18000, "url": "https://www.facebook.com/marketplace/item/1143491134389794/"},
    {"price": 4700, "year": 2003, "model": "sequoia TRD Sport SUV", "location": "Bakersfield, CA", "mileage": 130000, "url": "https://www.facebook.com/marketplace/item/1722297482482548/"},
    {"price": 86464, "year": 2026, "model": "sequoia Limited Sport Utility 4D", "location": "Glendale, CA", "mileage": 300, "url": "https://www.facebook.com/marketplace/item/1431288841780993/"},
    {"price": 5500, "year": 2003, "model": "sequoia", "location": "Bakersfield, CA", "mileage": 175000, "url": "https://www.facebook.com/marketplace/item/1625956068612928/"},
    {"price": 4000000, "year": 2002, "model": "sequoia SR5 Sport Utility 4D", "location": "Oxnard, CA", "mileage": 154000, "url": "https://www.facebook.com/marketplace/item/2116637542199801/", "note": "Likely typo - $4M"},
    {"price": 8750, "year": 2001, "model": "sequoia Limited Sport Utility 4D", "location": "Chatsworth, CA", "mileage": 300000, "url": "https://www.facebook.com/marketplace/item/1223810429663113/"},
    {"price": 6900, "year": 2006, "model": "sequoia limited v8", "location": "Lompoc, CA", "mileage": 222000, "url": "https://www.facebook.com/marketplace/item/2059424634816633/"},
    {"price": 6500, "original_price": 6900, "year": 2004, "model": "sequoia limited", "location": "Ukiah, CA", "mileage": 270000, "url": "https://www.facebook.com/marketplace/item/4099361300379157/"},
    {"price": 7000, "original_price": 10000, "year": 2004, "model": "sequoia SR5 Sport Utility 4D", "location": "Hawthorne, CA", "mileage": 267000, "url": "https://www.facebook.com/marketplace/item/1518765046236455/"},
    {"price": 38500, "year": 2017, "model": "sequoia Limited Sport Utility 4D", "location": "Sylmar, CA", "mileage": 80000, "url": "https://www.facebook.com/marketplace/item/4119811904927705/"},
    {"price": 42988, "year": 2020, "model": "sequoia sr5", "location": "Sparks, NV", "mileage": None, "url": "https://www.facebook.com/marketplace/item/754049991109289/"},
]

def normalize_model_name(model: str) -> str:
    """Normalize Sequoia model names"""
    model = model.strip().title()
    # Standardize common variations
    model = model.replace("Sequoia", "Sequoia")
    return model

def get_or_create_vehicle(cursor, year: int, model: str) -> int:
    """Get vehicle_id or create vehicle entry if it doesn't exist"""
    make = 'Toyota'
    trim = None

    # Extract trim from model if present
    model_lower = model.lower()
    if 'limited' in model_lower:
        trim = 'Limited'
        model = 'Sequoia'
    elif 'sr5' in model_lower:
        trim = 'SR5'
        model = 'Sequoia'
    elif 'capstone' in model_lower:
        trim = 'Capstone'
        model = 'Sequoia'
    elif 'trd' in model_lower:
        trim = 'TRD'
        model = 'Sequoia'
    else:
        model = 'Sequoia'

    # Check if vehicle exists
    cursor.execute("""
        SELECT id FROM vehicles
        WHERE make = ? AND model = ? AND year = ? AND (trim = ? OR (trim IS NULL AND ? IS NULL))
    """, (make, model, year, trim, trim))

    result = cursor.fetchone()
    if result:
        return result[0]

    # Create new vehicle entry
    cursor.execute("""
        INSERT INTO vehicles (make, model, year, trim, body_style, seating_capacity)
        VALUES (?, ?, ?, ?, 'SUV', 8)
    """, (make, model, year, trim))

    return cursor.lastrowid

def import_sequoia_listings(db_path: str = "car_valuation.db"):
    """Import Sequoia listings into the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    imported_count = 0
    skipped_count = 0

    for listing in SEQUOIA_LISTINGS:
        # Skip obvious data errors
        if listing['price'] > 100000 and listing['year'] < 2020:
            print(f"⚠️  Skipping suspicious listing: {listing['year']} {listing['model']} at ${listing['price']:,}")
            skipped_count += 1
            continue

        # Skip extremely low prices (likely partial listings)
        if listing['price'] < 1000:
            print(f"⚠️  Skipping low-price listing: {listing['year']} {listing['model']} at ${listing['price']}")
            skipped_count += 1
            continue

        # Extract location components
        location_parts = listing['location'].split(', ')
        city = location_parts[0] if location_parts else listing['location']
        state = location_parts[1] if len(location_parts) > 1 else 'CA'

        # Determine region
        region = 'California' if state == 'CA' else 'Nevada' if state == 'NV' else 'Other'

        # Normalize model name
        model = normalize_model_name(listing['model'])

        # Check if listing already exists (by URL)
        cursor.execute("""
            SELECT id FROM market_prices WHERE source_url = ?
        """, (listing['url'],))

        if cursor.fetchone():
            print(f"⏭️  Skipping duplicate: {listing['year']} {model}")
            skipped_count += 1
            continue

        # Get or create vehicle entry
        try:
            vehicle_id = get_or_create_vehicle(cursor, listing['year'], model)

            # Insert market price listing
            cursor.execute("""
                INSERT INTO market_prices (
                    vehicle_id, listing_date, mileage, asking_price,
                    city, state, region,
                    source, source_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                vehicle_id,
                datetime.now().date().isoformat(),
                listing.get('mileage', 0),
                listing['price'],
                city,
                state,
                region,
                'Facebook Marketplace',
                listing['url']
            ))

            print(f"✅ Imported: {listing['year']} {model} - ${listing['price']:,} - {city}, {state}")
            imported_count += 1

        except sqlite3.Error as e:
            print(f"❌ Error importing {listing['year']} {model}: {e}")
            skipped_count += 1

    conn.commit()
    conn.close()

    print(f"\n📊 Import Summary:")
    print(f"   ✅ Imported: {imported_count}")
    print(f"   ⏭️  Skipped: {skipped_count}")
    print(f"   📦 Total: {len(SEQUOIA_LISTINGS)}")

if __name__ == "__main__":
    print("🚗 Importing Toyota Sequoia listings from Facebook Marketplace scrape...\n")
    import_sequoia_listings()
    print("\n✨ Import complete!")
