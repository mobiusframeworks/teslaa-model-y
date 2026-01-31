#!/usr/bin/env python3
"""
Extract URLs from all Facebook RTF files and update database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from facebook_parser import FacebookParser
from database import DatabaseManager


def main():
    """Extract URLs from all RTF files"""

    parser = FacebookParser()
    db = DatabaseManager(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "car_valuation.db"))

    # All RTF files
    rtf_files = [
        "/Users/macmini/Desktop/lexus gx scrape 1:30.rtfd/TXT.rtf",
        "/Users/macmini/Desktop/gx scrape ca 1:30.rtfd/TXT.rtf",
        "/Users/macmini/Desktop/4 runner 4x4 scrape facebook 1:30.rtfd/TXT.rtf",
        "/Users/macmini/Desktop/tacoma scrape 1:30.rtfd/TXT.rtf",
        "/Users/macmini/Desktop/model y scrape west 1:30 fb market place.rtfd/TXT.rtf"
    ]

    print("="*80)
    print("EXTRACTING URLS FROM ALL RTF FILES".center(80))
    print("="*80)

    total_urls = 0
    total_updated = 0

    for rtf_path in rtf_files:
        if not os.path.exists(rtf_path):
            print(f"\n✗ File not found: {rtf_path}")
            continue

        print(f"\n{'='*80}")
        print(f"FILE: {os.path.basename(os.path.dirname(rtf_path))}")
        print(f"Path: {rtf_path}")
        print('='*80)

        # Extract URLs
        urls = parser.extract_urls_from_rtf(rtf_path)
        print(f"Found {len(urls)} URLs")
        total_urls += len(urls)

        if len(urls) > 0:
            print("\nSample URLs:")
            for url in urls[:3]:
                print(f"  {url[:80]}...")

    print(f"\n{'='*80}")
    print("EXTRACTION COMPLETE")
    print('='*80)
    print(f"Total URLs found: {total_urls}")

    # Check database status
    with db.get_connection() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM market_prices WHERE LENGTH(source_url) > 0")
        url_count = cursor.fetchone()[0]
        cursor = conn.execute("SELECT COUNT(*) FROM market_prices")
        total_count = cursor.fetchone()[0]

    print(f"\nDatabase Status:")
    print(f"  Total listings: {total_count}")
    print(f"  With URLs: {url_count}")
    print(f"  Without URLs: {total_count - url_count}")

    print(f"\n✓ Dashboard: http://localhost:8501")


if __name__ == "__main__":
    main()
