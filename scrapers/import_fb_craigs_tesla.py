#!/usr/bin/env python3
"""
Import Tesla listings from Facebook Marketplace Craigslist RTF
"""

import re
import sys
import sqlite3
from datetime import date
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from geolocation import get_closest_distance


def parse_facebook_rtf_manual(rtf_path):
    """Manually parse RTF with better accuracy"""

    with open(rtf_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Split by HYPERLINK to get individual listings
    listing_blocks = content.split('HYPERLINK')

    listings = []

    for block in listing_blocks[1:]:  # Skip first split which is header
        try:
            # Extract URL
            url_match = re.search(r'"([^"]+facebook\.com[^"]+)"', block)
            if not url_match:
                continue
            url = url_match.group(1)

            # Extract price - look for $X,XXX or $XX,XXX pattern
            price_match = re.search(r'\$([0-9,]+)', block)
            if not price_match:
                continue
            price_str = price_match.group(1).replace(',', '')
            price = int(price_str)

            # Skip obviously wrong prices
            if price < 5000 or price > 150000:
                continue

            # Extract vehicle info (year, make, model)
            vehicle_match = re.search(r'(20\d{2})\s+(Tesla)\s+(Model\s+[3SXY]|model\s+[3sxy])', block, re.IGNORECASE)
            if not vehicle_match:
                continue

            year = int(vehicle_match.group(1))
            make = "Tesla"
            model_raw = vehicle_match.group(3)

            # Normalize model name
            if 'model 3' in model_raw.lower():
                model = "Model 3"
            elif 'model s' in model_raw.lower():
                model = "Model S"
            elif 'model x' in model_raw.lower():
                model = "Model X"
            elif 'model y' in model_raw.lower():
                model = "Model Y"
            else:
                continue

            # Extract city - look for pattern: "City Name, CA"
            city_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*CA', block)
            city = city_match.group(1) if city_match else "Unknown"

            # Extract mileage if present
            mileage = None
            mileage_match = re.search(r'(\d+)K?\s*miles', block, re.IGNORECASE)
            if mileage_match:
                mileage_str = mileage_match.group(1).replace('K', '').replace(',', '')
                # If it's a small number, assume it's in thousands (like "19" means 19000)
                if mileage_match.group(0).endswith('K miles'):
                    mileage = int(mileage_str) * 1000
                else:
                    mileage = int(mileage_str)

            listing = {
                'year': year,
                'make': make,
                'model': model,
                'price': price,
                'mileage': mileage,
                'city': city,
                'state': 'CA',
                'source': 'facebook_marketplace',
                'source_url': url
            }

            listings.append(listing)

        except Exception as e:
            # Skip problematic blocks
            continue

    return listings


def import_listings(listings, db_path="car_valuation.db"):
    """Import listings into database"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    imported = 0
    skipped = 0

    for listing in listings:
        try:
            # Get or create vehicle
            cursor.execute("""
                SELECT id FROM vehicles
                WHERE year = ? AND make = ? AND model = ?
            """, (listing['year'], listing['make'], listing['model']))

            vehicle = cursor.fetchone()

            if vehicle:
                vehicle_id = vehicle[0]
            else:
                cursor.execute("""
                    INSERT INTO vehicles (year, make, model, trim)
                    VALUES (?, ?, ?, ?)
                """, (listing['year'], listing['make'], listing['model'], None))
                vehicle_id = cursor.lastrowid

            # Check if listing already exists (by URL)
            if listing['source_url']:
                cursor.execute("""
                    SELECT id FROM market_prices WHERE source_url = ?
                """, (listing['source_url'],))

                if cursor.fetchone():
                    skipped += 1
                    continue

            # Calculate distance
            distance = get_closest_distance(listing['city'], listing['state'])

            # Insert listing
            cursor.execute("""
                INSERT INTO market_prices (
                    vehicle_id, asking_price, mileage, city, state,
                    source, source_url, distance_miles, listing_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                vehicle_id,
                listing['price'],
                listing['mileage'],
                listing['city'],
                listing['state'],
                listing['source'],
                listing['source_url'],
                distance,
                date.today().isoformat()
            ))

            imported += 1
            print(f"✓ Imported: {listing['year']} {listing['make']} {listing['model']} - ${listing['price']:,} - {listing['city']}")

        except Exception as e:
            print(f"✗ Error importing listing: {e}")
            skipped += 1

    conn.commit()
    conn.close()

    return imported, skipped


if __name__ == '__main__':
    rtf_path = "/Users/macmini/Desktop/mdely y craigs.rtfd/TXT.rtf"

    print("Parsing Facebook Marketplace listings...")
    listings = parse_facebook_rtf_manual(rtf_path)

    print(f"\nFound {len(listings)} valid listings:")
    for listing in listings:
        mileage_str = f"{listing['mileage']:,} mi" if listing['mileage'] else "Unknown mi"
        print(f"  {listing['year']} {listing['make']} {listing['model']} - ${listing['price']:,} - {mileage_str} - {listing['city']}, {listing['state']}")

    print("\n" + "="*80)
    print("Importing into database...")
    print("="*80)

    imported, skipped = import_listings(listings)

    print(f"\n{'='*80}")
    print(f"✓ Imported: {imported} new listings")
    print(f"⊘ Skipped: {skipped} duplicates")
    print(f"{'='*80}")
