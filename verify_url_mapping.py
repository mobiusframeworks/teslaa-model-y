#!/usr/bin/env python3
"""
Verify URL to Listing Mapping
Check if URLs are correctly matched to their listings
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager
import re


def extract_listing_id_from_url(url):
    """Extract the Facebook listing ID from URL"""
    match = re.search(r'/item/(\d+)', url)
    return match.group(1) if match else None


def verify_mappings(db_path="car_valuation.db"):
    """Verify URL mappings are correct"""

    db = DatabaseManager(db_path)

    print("="*80)
    print("VERIFYING URL TO LISTING MAPPINGS")
    print("="*80)

    # Get sample of listings with URLs
    query = """
        SELECT
            mp.id,
            v.year,
            v.make,
            v.model,
            mp.asking_price,
            mp.mileage,
            mp.city,
            mp.state,
            mp.source_url
        FROM market_prices mp
        JOIN vehicles v ON mp.vehicle_id = v.id
        WHERE LENGTH(mp.source_url) > 0
        ORDER BY mp.id
        LIMIT 20
    """

    with db.get_connection() as conn:
        cursor = conn.execute(query)
        listings = cursor.fetchall()

    print(f"\nChecking {len(listings)} listings with URLs...\n")

    for listing in listings:
        lid, year, make, model, price, mileage, city, state, url = listing
        fb_id = extract_listing_id_from_url(url)

        print(f"ID {lid}: {year} {make} {model} - ${price:,.0f} @ {mileage:,}mi")
        print(f"  Location: {city}, {state}")
        print(f"  FB Listing: {fb_id}")
        print(f"  URL: {url[:70]}...")
        print()

    print("="*80)
    print("POTENTIAL ISSUES TO CHECK")
    print("="*80)
    print("""
The URLs are assigned in the order they appear in the RTF file.
The listings are parsed in the order they appear in the text file.

If these orders don't match, URLs will be mismatched!

To verify manually:
1. Pick a listing from above (e.g., ID 1)
2. Open the Facebook URL in your browser
3. Check if the vehicle matches the database entry
4. If it doesn't match, URLs are out of order

Common causes of mismatch:
- Price filtering removed some listings but not their URLs
- RTF and text extraction ordered differently
- Duplicate removal affected order

If URLs are wrong, we need to re-import with better URL matching.
    """)

    # Check for duplicate URLs
    query_dupes = """
        SELECT source_url, COUNT(*) as count
        FROM market_prices
        WHERE LENGTH(source_url) > 0
        GROUP BY source_url
        HAVING count > 1
    """

    with db.get_connection() as conn:
        cursor = conn.execute(query_dupes)
        dupes = cursor.fetchall()

    if dupes:
        print("\n⚠ WARNING: Found duplicate URLs!")
        print("These URLs are assigned to multiple listings:")
        for url, count in dupes[:5]:
            print(f"  {url[:60]}... ({count} times)")
    else:
        print("\n✓ No duplicate URLs found")

    # Check for sequential URL assignment issues
    print("\n" + "="*80)
    print("URL ASSIGNMENT PATTERN CHECK")
    print("="*80)

    with db.get_connection() as conn:
        # Group by source file/batch (approximate based on ID ranges)
        cursor = conn.execute("""
            SELECT
                CASE
                    WHEN mp.id <= 191 THEN 'Batch 1 (IDs 1-191)'
                    WHEN mp.id <= 272 THEN 'Batch 2 (IDs 192-272)'
                    ELSE 'Batch 3 (IDs 273+)'
                END as batch,
                COUNT(*) as total_listings,
                COUNT(CASE WHEN LENGTH(source_url) > 0 THEN 1 END) as with_urls,
                ROUND(100.0 * COUNT(CASE WHEN LENGTH(source_url) > 0 THEN 1 END) / COUNT(*), 1) as url_pct
            FROM market_prices mp
            GROUP BY batch
            ORDER BY MIN(mp.id)
        """)
        batches = cursor.fetchall()

        print("\nURL coverage by batch:")
        for batch, total, with_urls, pct in batches:
            print(f"  {batch}: {with_urls}/{total} ({pct}%)")


if __name__ == "__main__":
    verify_mappings()
