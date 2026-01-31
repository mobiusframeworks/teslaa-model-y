#!/usr/bin/env python3
"""
Update ALL database listings with URLs from RTF files
Matches each listing with its corresponding URL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from facebook_parser import FacebookParser
from database import DatabaseManager


def process_file_with_urls(parser, db, rtf_path, txt_path, description):
    """Process a single file and match URLs to listings"""

    print(f"\n{'='*80}")
    print(f"PROCESSING: {description}")
    print('='*80)

    # Extract URLs from RTF
    urls = parser.extract_urls_from_rtf(rtf_path)
    print(f"URLs in RTF: {len(urls)}")

    # Parse the text file to get listings (already filtered)
    listings = parser.parse_facebook_text(txt_path, min_price=0, max_price=1000000)  # No price filter for matching
    print(f"Listings parsed: {len(listings)}")

    # Match URLs to listings
    update_count = 0
    for i, listing in enumerate(listings):
        if i < len(urls):
            listing['source_url'] = urls[i]

            # Update database
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
                        print(f"✓ {listing['year']} {listing['make']} {listing['model']} - ${listing['price']:,}")
                    else:
                        print(f"⚠ Not in DB: {listing['year']} {listing['make']} {listing['model']} - ${listing['price']:,}")

            except Exception as e:
                print(f"✗ Error: {e}")

    return update_count


def main():
    """Update all listings with URLs"""

    parser = FacebookParser()
    db = DatabaseManager(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "car_valuation.db"))

    # All file pairs (RTF + TXT)
    files = [
        {
            'rtf': "/Users/macmini/Desktop/lexus gx scrape 1:30.rtfd/TXT.rtf",
            'txt': "/tmp/gx_scrape.txt",
            'description': "Lexus GX Scrape #1"
        },
        {
            'rtf': "/Users/macmini/Desktop/gx scrape ca 1:30.rtfd/TXT.rtf",
            'txt': "/tmp/gx_ca_scrape.txt",
            'description': "Lexus GX California Scrape"
        },
        {
            'rtf': "/Users/macmini/Desktop/4 runner 4x4 scrape facebook 1:30.rtfd/TXT.rtf",
            'txt': "/tmp/4runner_scrape.txt",
            'description': "Toyota 4Runner 4x4"
        },
        {
            'rtf': "/Users/macmini/Desktop/tacoma scrape 1:30.rtfd/TXT.rtf",
            'txt': "/tmp/tacoma_scrape.txt",
            'description': "Toyota Tacoma"
        },
        {
            'rtf': "/Users/macmini/Desktop/model y scrape west 1:30 fb market place.rtfd/TXT.rtf",
            'txt': "/tmp/model_y_scrape.txt",
            'description': "Tesla Model Y West"
        }
    ]

    print("="*80)
    print("UPDATING ALL LISTINGS WITH URLS".center(80))
    print("="*80)

    total_updated = 0

    for file_info in files:
        if not os.path.exists(file_info['rtf']):
            print(f"\n✗ RTF not found: {file_info['rtf']}")
            continue

        if not os.path.exists(file_info['txt']):
            print(f"\n✗ TXT not found: {file_info['txt']}")
            # Try to create it from RTF
            continue

        count = process_file_with_urls(
            parser,
            db,
            file_info['rtf'],
            file_info['txt'],
            file_info['description']
        )

        total_updated += count
        print(f"Updated: {count}")

    # Final status
    print(f"\n{'='*80}")
    print("UPDATE COMPLETE")
    print('='*80)
    print(f"Total URLs updated: {total_updated}")

    # Verify
    with db.get_connection() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM market_prices WHERE LENGTH(source_url) > 0")
        url_count = cursor.fetchone()[0]
        cursor = conn.execute("SELECT COUNT(*) FROM market_prices")
        total_count = cursor.fetchone()[0]

    print(f"\nDatabase Status:")
    print(f"  Total listings: {total_count}")
    print(f"  With URLs: {url_count} ({url_count/total_count*100:.1f}%)")
    print(f"  Without URLs: {total_count - url_count}")

    print(f"\n✓ View with clickable links: http://localhost:8501")


if __name__ == "__main__":
    main()
