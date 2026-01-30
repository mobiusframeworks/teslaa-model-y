#!/usr/bin/env python3
"""
Import San Jose Area Facebook Scrapes
4 new scrapes from 100 mile radius around San Jose
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from facebook_parser import FacebookParser
from database import DatabaseManager


def process_file_with_urls(parser, db, rtf_path, txt_path, description):
    """Process a single file and match URLs to listings"""

    print(f"\n{'='*80}")
    print(f"FILE: {description}")
    print(f"RTF: {rtf_path}")
    print(f"TXT: {txt_path}")
    print('='*80)

    if not os.path.exists(rtf_path):
        print(f"✗ RTF file not found: {rtf_path}")
        return 0

    if not os.path.exists(txt_path):
        print(f"✗ Text file not found: {txt_path}")
        return 0

    # Extract URLs from RTF
    print("\nExtracting URLs from RTF...")
    urls = parser.extract_urls_from_rtf(rtf_path)
    print(f"Found {len(urls)} URLs")

    # Parse text file with URLs
    print("\nParsing listings from text...")
    listings = parser.parse_facebook_text(txt_path)

    # Match URLs to listings
    print(f"\nMatching URLs to {len(listings)} listings...")
    for i, listing in enumerate(listings):
        if i < len(urls):
            listing['source_url'] = urls[i]

    print(f"\n✓ Parsed {len(listings)} listings")
    urls_matched = sum(1 for l in listings if l.get('source_url'))
    print(f"  URLs matched: {urls_matched}/{len(listings)}")

    # Load to database with deduplication and distance calculation
    print(f"\nLoading to database...")
    stats = parser.load_to_database(listings, deduplicate=True)

    return stats['loaded']


def main():
    """Import San Jose area scrapes"""

    parser = FacebookParser()
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "car_valuation.db")
    db = DatabaseManager(db_path)

    # San Jose area files (100 mile radius)
    files = [
        {
            'rtf': "/Users/macmini/Desktop/highlander scrape 1:30 san jose.rtfd/TXT.rtf",
            'txt': "/tmp/highlander_sj_scrape.txt",
            'description': "Toyota Highlander (San Jose 100mi)"
        },
        {
            'rtf': "/Users/macmini/Desktop/lexus gx scrape san jose.rtfd/TXT.rtf",
            'txt': "/tmp/gx_sj_scrape.txt",
            'description': "Lexus GX (San Jose 100mi)"
        },
        {
            'rtf': "/Users/macmini/Desktop/sequoia 4x4 scraoe.rtfd/TXT.rtf",
            'txt': "/tmp/sequoia_scrape.txt",
            'description': "Toyota Sequoia 4x4 (San Jose 100mi)"
        },
        {
            'rtf': "/Users/macmini/Desktop/4 runner scrape san jose 1:30.rtfd/TXT.rtf",
            'txt': "/tmp/4runner_sj_scrape.txt",
            'description': "Toyota 4Runner (San Jose 100mi)"
        }
    ]

    print("="*80)
    print("SAN JOSE AREA BATCH IMPORT - 100 Mile Radius".center(80))
    print("="*80)

    total_stats = {
        'files': 0,
        'total_parsed': 0,
        'total_loaded': 0,
        'total_duplicates': 0,
        'total_urls': 0
    }

    for file_info in files:
        total_stats['files'] += 1
        loaded = process_file_with_urls(
            parser,
            db,
            file_info['rtf'],
            file_info['txt'],
            file_info['description']
        )
        total_stats['total_loaded'] += loaded

    # Final summary
    print(f"\n{'='*80}")
    print("BATCH IMPORT COMPLETE")
    print('='*80)
    print(f"Files Processed: {total_stats['files']}")
    print(f"New Listings Loaded: {total_stats['total_loaded']}")

    # Database summary
    with db.get_connection() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM market_prices WHERE LENGTH(source_url) > 0")
        url_count = cursor.fetchone()[0]

        cursor = conn.execute("SELECT COUNT(*) FROM market_prices WHERE distance_miles IS NOT NULL")
        distance_count = cursor.fetchone()[0]

        cursor = conn.execute("SELECT COUNT(*) FROM market_prices WHERE distance_miles <= 100")
        nearby_count = cursor.fetchone()[0]

        cursor = conn.execute("SELECT COUNT(*) FROM market_prices")
        total_count = cursor.fetchone()[0]

    print(f"\n{'='*80}")
    print("DATABASE SUMMARY")
    print('='*80)
    print(f"Total Listings: {total_count}")
    print(f"With URLs: {url_count} ({url_count/total_count*100:.1f}%)")
    print(f"With Distance Data: {distance_count}")
    print(f"Within 100 Miles (Santa Cruz/San Jose): {nearby_count}")

    # Show vehicle breakdown
    print(f"\n{'='*80}")
    print("NEW LISTINGS BY VEHICLE")
    print('='*80)

    query = """
        SELECT
            v.make,
            v.model,
            COUNT(*) as count,
            MIN(mp.asking_price) as min_price,
            MAX(mp.asking_price) as max_price,
            AVG(mp.asking_price) as avg_price,
            MIN(mp.distance_miles) as closest
        FROM market_prices mp
        JOIN vehicles v ON mp.vehicle_id = v.id
        WHERE mp.source = 'facebook_marketplace'
        GROUP BY v.make, v.model
        ORDER BY count DESC
    """

    with db.get_connection() as conn:
        cursor = conn.execute(query)
        results = cursor.fetchall()

        print(f"{'Make/Model':<30} {'Count':<8} {'Price Range':<25} {'Closest':<10}")
        print("-" * 80)

        for row in results:
            make, model, count, min_p, max_p, avg_p, closest = row
            vehicle = f"{make} {model}"
            price_range = f"${min_p:,.0f} - ${max_p:,.0f}"
            closest_str = f"{closest:.0f}mi" if closest else "N/A"
            print(f"{vehicle:<30} {count:<8} {price_range:<25} {closest_str:<10}")

    print(f"\n{'='*80}")
    print("✓ View in dashboard: http://localhost:8501")
    print("✓ Use Distance Filter to see only nearby listings")


if __name__ == "__main__":
    main()
