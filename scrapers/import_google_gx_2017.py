#!/usr/bin/env python3
"""
Import Google Search Results - 2017 Lexus GX
Import vehicle listings from Google Shopping search results
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_parser import extract_urls_from_google_rtf, parse_google_listings
from database import DatabaseManager
from geolocation import get_closest_distance


def import_google_listings(listings, db_path="../car_valuation.db"):
    """Import Google listings into database"""

    db = DatabaseManager(db_path)

    stats = {
        'total': len(listings),
        'loaded': 0,
        'duplicates': 0,
        'errors': 0
    }

    with db.get_connection() as conn:
        for listing in listings:
            try:
                # Get or create vehicle
                cursor = conn.execute("""
                    SELECT id FROM vehicles
                    WHERE year = ? AND make = ? AND model = ?
                """, (listing['year'], listing['make'], listing['model']))

                vehicle = cursor.fetchone()

                if vehicle:
                    vehicle_id = vehicle[0]
                else:
                    # Create vehicle
                    cursor = conn.execute("""
                        INSERT INTO vehicles (year, make, model, trim)
                        VALUES (?, ?, ?, ?)
                    """, (listing['year'], listing['make'], listing['model'], ''))
                    vehicle_id = cursor.lastrowid

                # Check for duplicate listing
                cursor = conn.execute("""
                    SELECT id FROM market_prices
                    WHERE vehicle_id = ?
                      AND asking_price = ?
                      AND mileage = ?
                      AND city = ?
                      AND state = ?
                """, (vehicle_id, listing['price'], listing['mileage'],
                      listing['city'], listing['state']))

                if cursor.fetchone():
                    stats['duplicates'] += 1
                    print(f"  ⚠ Duplicate: {listing['year']} {listing['make']} {listing['model']} - ${listing['price']:,.0f}")
                    continue

                # Calculate distance
                distance = None
                if listing['city'] and listing['state']:
                    distance = get_closest_distance(listing['city'], listing['state'])

                # Insert market price
                from datetime import date
                conn.execute("""
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
                    listing.get('source_url'),
                    distance,
                    date.today().isoformat()
                ))

                stats['loaded'] += 1

                url_status = "✓" if listing.get('source_url') else "✗"
                dist_str = f"{distance:.0f}mi" if distance else "N/A"
                print(f"  {url_status} Loaded: {listing['year']} {listing['make']} {listing['model']} - "
                      f"${listing['price']:,.0f} @ {listing['mileage']:,}mi ({dist_str})")

            except Exception as e:
                stats['errors'] += 1
                print(f"  ✗ Error: {listing['year']} {listing['make']} {listing['model']} - {e}")

        conn.commit()

    return stats


def main():
    """Import 2017 Lexus GX listings from Google"""

    rtf_path = "/Users/macmini/Desktop/lexus x scrape 2017 google.rtfd/TXT.rtf"
    txt_path = "/tmp/lexus_gx_2017_google.txt"

    print("="*80)
    print("IMPORTING GOOGLE LISTINGS - 2017 Lexus GX")
    print("="*80)

    # Convert RTF to text if needed
    import subprocess
    print("\n1. Converting RTF to text...")
    subprocess.run([
        'textutil', '-convert', 'txt',
        rtf_path,
        '-output', txt_path
    ], check=True)
    print("   ✓ Converted")

    # Extract URLs
    print("\n2. Extracting URLs from RTF...")
    urls = extract_urls_from_google_rtf(rtf_path)
    print(f"   Found {len(urls)} URLs")

    # Parse listings
    print("\n3. Parsing listings from text...")
    listings = parse_google_listings(txt_path)
    print(f"   Found {len(listings)} listings")

    # Match URLs to listings
    print("\n4. Matching URLs to listings...")
    for i, listing in enumerate(listings):
        if i < len(urls):
            listing['source_url'] = urls[i]

    urls_matched = sum(1 for l in listings if l.get('source_url'))
    print(f"   Matched {urls_matched}/{len(listings)} URLs")

    # Import to database
    print("\n5. Importing to database...")
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "car_valuation.db")
    stats = import_google_listings(listings, db_path)

    # Summary
    print(f"\n{'='*80}")
    print("IMPORT COMPLETE")
    print(f"{'='*80}")
    print(f"Total listings: {stats['total']}")
    print(f"Successfully loaded: {stats['loaded']}")
    print(f"Duplicates skipped: {stats['duplicates']}")
    print(f"Errors: {stats['errors']}")

    # Database stats
    db = DatabaseManager(db_path)
    with db.get_connection() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM market_prices")
        total_listings = cursor.fetchone()[0]

        cursor = conn.execute("SELECT COUNT(*) FROM market_prices WHERE LENGTH(source_url) > 0")
        with_urls = cursor.fetchone()[0]

        cursor = conn.execute("""
            SELECT COUNT(*) FROM market_prices mp
            JOIN vehicles v ON mp.vehicle_id = v.id
            WHERE v.make = 'Lexus' AND v.model LIKE '%GX%'
        """)
        gx_count = cursor.fetchone()[0]

    print(f"\n{'='*80}")
    print("DATABASE SUMMARY")
    print(f"{'='*80}")
    print(f"Total listings: {total_listings}")
    print(f"With URLs: {with_urls} ({with_urls/total_listings*100:.1f}%)")
    print(f"Lexus GX listings: {gx_count}")

    print(f"\n✓ View in dashboard: http://localhost:8501")


if __name__ == "__main__":
    main()
