#!/usr/bin/env python3
"""
Import Tesla listings from Carvana RTF
"""

import re
import sys
import sqlite3
from datetime import date
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from geolocation import get_closest_distance


def parse_carvana_rtf(rtf_path):
    """Parse Carvana RTF file for Tesla listings"""

    with open(rtf_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Split by HYPERLINK to get individual listings
    listing_blocks = content.split('HYPERLINK')

    listings = []

    for block in listing_blocks[1:]:  # Skip first split which is header
        try:
            # Extract URL - look for carvana.com URLs
            url_match = re.search(r'"(https://www\.carvana\.com/vehicle/[^"]+)"', block)
            if not url_match:
                continue
            url = url_match.group(1)

            # Extract vehicle info (year, make, model)
            # Look for pattern like: 2024\'a0Tesla\'a0Model Y
            vehicle_match = re.search(r'(20\d{2})\\\'a0(Tesla)\\\'a0(Model\s+[YS3X])', block, re.IGNORECASE)
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

            # Extract trim (Standard, Long Range, Performance)
            trim = None
            trim_match = re.search(r'\\strokec4\s+(Standard|Long Range|Performance)', block)
            if trim_match:
                trim = trim_match.group(1)

            # Extract price - look for $XX,XXX pattern
            price_match = re.search(r'\$([0-9,]+)\\cb1', block)
            if not price_match:
                continue
            price_str = price_match.group(1).replace(',', '')
            price = int(price_str)

            # Skip obviously wrong prices
            if price < 5000 or price > 150000:
                continue

            # Extract mileage - look for "XXk\'a0miles" pattern
            mileage = None
            mileage_match = re.search(r'(\d+)k\\\'a0miles', block, re.IGNORECASE)
            if mileage_match:
                mileage_str = mileage_match.group(1)
                mileage = int(mileage_str) * 1000

            # Carvana is national, but we'll use "Unknown" for city
            city = "Various"
            state = "Nationwide"

            listing = {
                'year': year,
                'make': make,
                'model': model,
                'trim': trim,
                'price': price,
                'mileage': mileage,
                'city': city,
                'state': state,
                'source': 'carvana',
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
                WHERE year = ? AND make = ? AND model = ? AND trim = ?
            """, (listing['year'], listing['make'], listing['model'], listing['trim']))

            vehicle = cursor.fetchone()

            if vehicle:
                vehicle_id = vehicle[0]
            else:
                cursor.execute("""
                    INSERT INTO vehicles (year, make, model, trim)
                    VALUES (?, ?, ?, ?)
                """, (listing['year'], listing['make'], listing['model'], listing['trim']))
                vehicle_id = cursor.lastrowid

            # Check if listing already exists (by URL)
            if listing['source_url']:
                cursor.execute("""
                    SELECT id FROM market_prices WHERE source_url = ?
                """, (listing['source_url'],))

                if cursor.fetchone():
                    skipped += 1
                    continue

            # Calculate distance (use None for nationwide)
            distance = None

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
            mileage_str = f"{listing['mileage']:,} mi" if listing['mileage'] else "Unknown mi"
            trim_str = f" ({listing['trim']})" if listing['trim'] else ""
            print(f"✓ Imported: {listing['year']} {listing['make']} {listing['model']}{trim_str} - ${listing['price']:,} - {mileage_str}")

        except Exception as e:
            print(f"✗ Error importing listing: {e}")
            skipped += 1

    conn.commit()
    conn.close()

    return imported, skipped


if __name__ == '__main__':
    rtf_path = "/Users/macmini/Desktop/tesla 2024 carvana.rtfd/TXT.rtf"

    print("Parsing Carvana listings...")
    listings = parse_carvana_rtf(rtf_path)

    print(f"\nFound {len(listings)} valid listings:")
    for listing in listings:
        mileage_str = f"{listing['mileage']:,} mi" if listing['mileage'] else "Unknown mi"
        trim_str = f" ({listing['trim']})" if listing['trim'] else ""
        print(f"  {listing['year']} {listing['make']} {listing['model']}{trim_str} - ${listing['price']:,} - {mileage_str}")

    print("\n" + "="*80)
    print("Importing into database...")
    print("="*80)

    imported, skipped = import_listings(listings)

    print(f"\n{'='*80}")
    print(f"✓ Imported: {imported} new listings")
    print(f"⊘ Skipped: {skipped} duplicates")
    print(f"{'='*80}")
