#!/usr/bin/env python3
"""
Re-import Facebook Marketplace data with URLs
This script extracts URLs from original RTF files
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from facebook_parser import FacebookParser


def main():
    """Re-import with URLs from RTF files"""

    parser = FacebookParser()

    # Original RTF files with their text conversions
    files = [
        {
            'rtf': "/Users/macmini/Desktop/tacoma scrape 1:30.rtfd/TXT.rtf",
            'txt': "/tmp/tacoma_scrape.txt",
            'description': "Toyota Tacoma Scrape"
        },
        {
            'rtf': "/Users/macmini/Desktop/model y scrape west 1:30 fb market place.rtfd/TXT.rtf",
            'txt': "/tmp/model_y_scrape.txt",
            'description': "Tesla Model Y West Coast"
        }
    ]

    print("="*80)
    print("RE-IMPORTING WITH URLS FROM RTF FILES".center(80))
    print("="*80)

    all_listings = []

    for file_info in files:
        rtf_path = file_info['rtf']
        txt_path = file_info['txt']
        description = file_info['description']

        print(f"\n{'='*80}")
        print(f"FILE: {description}")
        print(f"RTF: {rtf_path}")
        print(f"TXT: {txt_path}")
        print('='*80)

        if not os.path.exists(rtf_path):
            print(f"✗ RTF file not found: {rtf_path}")
            continue

        if not os.path.exists(txt_path):
            print(f"✗ Text file not found: {txt_path}")
            continue

        # Extract URLs from RTF
        print("\nExtracting URLs from RTF...")
        urls = parser.extract_urls_from_rtf(rtf_path)
        print(f"Found {len(urls)} URLs")

        # Parse text file
        print("\nParsing listings from text...")
        listings = parser.parse_facebook_text(txt_path)

        # Match URLs to listings
        print(f"\nMatching URLs to {len(listings)} listings...")
        for i, listing in enumerate(listings):
            if i < len(urls):
                listing['source_url'] = urls[i]
                print(f"  ✓ URL matched for {listing['year']} {listing['make']} {listing['model']}")
            else:
                print(f"  ⚠ No URL for {listing['year']} {listing['make']} {listing['model']}")

        all_listings.extend(listings)

        print(f"\n✓ Processed {len(listings)} listings from {description}")
        urls_matched = sum(1 for l in listings if l.get('source_url'))
        print(f"  URLs matched: {urls_matched}/{len(listings)}")

    # Clear old entries and reload
    print(f"\n{'='*80}")
    print("UPDATING DATABASE WITH URLS")
    print('='*80)

    # Update existing entries with URLs
    from database import DatabaseManager
    db = DatabaseManager(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "car_valuation.db"))

    update_count = 0
    for listing in all_listings:
        if not listing.get('source_url'):
            continue

        # Find matching market_price entry - first get the ID
        try:
            with db.get_connection() as conn:
                # Find the listing ID
                select_query = """
                    SELECT mp.id
                    FROM market_prices mp
                    JOIN vehicles v ON mp.vehicle_id = v.id
                    WHERE v.make = ?
                      AND v.model = ?
                      AND v.year = ?
                      AND mp.asking_price = ?
                      AND mp.mileage = ?
                      AND (mp.source_url IS NULL OR mp.source_url = '')
                    LIMIT 1
                """

                cursor = conn.execute(select_query, (
                    listing['make'],
                    listing['model'],
                    listing['year'],
                    listing['price'],
                    listing.get('mileage', 0)
                ))
                result = cursor.fetchone()

                if result:
                    listing_id = result[0]

                    # Update with URL
                    update_query = "UPDATE market_prices SET source_url = ? WHERE id = ?"
                    conn.execute(update_query, (listing['source_url'], listing_id))

                    update_count += 1
                    print(f"✓ Updated: {listing['year']} {listing['make']} {listing['model']} - ${listing['price']:,}")
                else:
                    print(f"⚠ Not found: {listing['year']} {listing['make']} {listing['model']} - ${listing['price']:,}")

        except Exception as e:
            print(f"✗ Error updating: {e}")

    print(f"\n{'='*80}")
    print("UPDATE COMPLETE")
    print('='*80)
    print(f"Total listings processed: {len(all_listings)}")
    print(f"URLs updated in database: {update_count}")

    # Verify
    with db.get_connection() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM market_prices WHERE LENGTH(source_url) > 0")
        url_count = cursor.fetchone()[0]
        cursor = conn.execute("SELECT COUNT(*) FROM market_prices")
        total_count = cursor.fetchone()[0]

    print(f"\nDatabase Status:")
    print(f"  Total listings: {total_count}")
    print(f"  With URLs: {url_count}")
    print(f"  Without URLs: {total_count - url_count}")

    print(f"\n✓ View in dashboard: http://localhost:8501")


if __name__ == "__main__":
    main()
