#!/usr/bin/env python3
"""
Batch Facebook Import
Import multiple Facebook scrape files at once
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from facebook_parser import FacebookParser


def main():
    """Import multiple Facebook scrape files"""

    parser = FacebookParser()

    # Files to import
    files = [
        ("/tmp/model_y_scrape.txt", "Tesla Model Y West Coast Scrape"),
        ("/tmp/tacoma_scrape.txt", "Toyota Tacoma Scrape"),
    ]

    print("="*80)
    print("BATCH FACEBOOK IMPORT - Multiple Files".center(80))
    print("="*80)

    all_listings = []
    total_stats = {
        'files': 0,
        'total_parsed': 0,
        'total_loaded': 0,
        'total_duplicates': 0,
        'total_skipped': 0,
        'total_errors': 0
    }

    # Parse all files
    for filepath, description in files:
        print(f"\n{'='*80}")
        print(f"FILE: {description}")
        print(f"Path: {filepath}")
        print('='*80)

        if not os.path.exists(filepath):
            print(f"✗ File not found: {filepath}")
            continue

        # Parse
        listings = parser.parse_facebook_text(filepath)
        all_listings.extend(listings)

        print(f"\n✓ Parsed {len(listings)} listings from {description}")

        # Show vehicle breakdown
        makes = {}
        for listing in listings:
            make = listing.get('make', 'Unknown')
            makes[make] = makes.get(make, 0) + 1

        print("\nBy Make:")
        for make, count in sorted(makes.items(), key=lambda x: x[1], reverse=True):
            print(f"  {make}: {count}")

        total_stats['files'] += 1
        total_stats['total_parsed'] += len(listings)

    # Load all to database (with deduplication)
    print(f"\n{'='*80}")
    print("LOADING ALL LISTINGS TO DATABASE")
    print('='*80)
    print(f"\nTotal listings collected: {len(all_listings)}")
    print("Deduplicating and loading...")

    stats = parser.load_to_database(all_listings, deduplicate=True)

    total_stats['total_loaded'] = stats['loaded']
    total_stats['total_duplicates'] = stats['duplicates']
    total_stats['total_skipped'] = stats['skipped']
    total_stats['total_errors'] = stats['errors']

    # Final summary
    print(f"\n{'='*80}")
    print("BATCH IMPORT COMPLETE")
    print('='*80)
    print(f"\nFiles Processed: {total_stats['files']}")
    print(f"Total Parsed: {total_stats['total_parsed']}")
    print(f"Loaded to DB: {total_stats['total_loaded']}")
    print(f"Duplicates Removed: {total_stats['total_duplicates']}")
    print(f"Skipped: {total_stats['total_skipped']}")
    print(f"Errors: {total_stats['total_errors']}")

    if total_stats['total_loaded'] > 0:
        success_rate = (total_stats['total_loaded'] / total_stats['total_parsed']) * 100
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        print(f"\n✓ Successfully imported {total_stats['total_loaded']} NEW listings!")

        # Show what was added
        print(f"\n{'='*80}")
        print("NEW DATA SUMMARY")
        print('='*80)

        # Query database for latest additions
        from database import DatabaseManager
        db = DatabaseManager()

        query = """
            SELECT
                v.make,
                v.model,
                COUNT(*) as count,
                MIN(mp.asking_price) as min_price,
                MAX(mp.asking_price) as max_price,
                AVG(mp.asking_price) as avg_price
            FROM market_prices mp
            JOIN vehicles v ON mp.vehicle_id = v.id
            WHERE mp.source = 'facebook_marketplace'
            GROUP BY v.make, v.model
            ORDER BY count DESC
        """

        with db.get_connection() as conn:
            cursor = conn.execute(query)
            results = cursor.fetchall()

            print("\nVehicles in Database (from Facebook):")
            print(f"{'Make/Model':<30} {'Count':<8} {'Price Range':<25} {'Average':<12}")
            print("-" * 80)

            for row in results:
                make, model, count, min_p, max_p, avg_p = row
                vehicle = f"{make} {model}"
                price_range = f"${min_p:,.0f} - ${max_p:,.0f}"
                avg = f"${avg_p:,.0f}"
                print(f"{vehicle:<30} {count:<8} {price_range:<25} {avg:<12}")

        print(f"\n{'='*80}")
        print("\n✓ View in dashboard: http://localhost:8501")
        print("✓ Or CLI: python3 car_finder.py -> [3] View All Listings")


if __name__ == "__main__":
    main()
