#!/usr/bin/env python3
"""
Deduplicate Market Listings
Remove duplicate listings, preferring entries with URLs
"""

import sqlite3
import sys


def deduplicate_database(db_path="car_valuation.db"):
    """Remove duplicate market_prices entries"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("="*80)
    print("DEDUPLICATING MARKET LISTINGS")
    print("="*80)

    # Step 1: Find duplicates
    print("\n1. Finding duplicate listings...")

    cursor.execute("""
        SELECT
            vehicle_id,
            asking_price,
            mileage,
            city,
            state,
            COUNT(*) as count,
            GROUP_CONCAT(id) as ids,
            GROUP_CONCAT(CASE WHEN LENGTH(source_url) > 0 THEN id END) as ids_with_urls
        FROM market_prices
        GROUP BY vehicle_id, asking_price, mileage, city, state
        HAVING count > 1
        ORDER BY vehicle_id, asking_price
    """)

    duplicates = cursor.fetchall()

    if not duplicates:
        print("✓ No duplicates found. Database is clean.")
        conn.close()
        return

    print(f"\nFound {len(duplicates)} groups of duplicate listings")

    # Step 2: Remove duplicates, keeping entries with URLs
    print("\n2. Removing duplicates...")

    total_deleted = 0

    for vehicle_id, price, mileage, city, state, count, ids_str, ids_with_urls_str in duplicates:
        ids = [int(x) for x in ids_str.split(',')]

        # Get vehicle details for display
        cursor.execute("""
            SELECT make, model, year
            FROM vehicles
            WHERE id = ?
        """, (vehicle_id,))
        make, model, year = cursor.fetchone()

        # Determine which ID to keep
        if ids_with_urls_str:
            # Keep the one with URL
            ids_with_urls = [int(x) for x in ids_with_urls_str.split(',')]
            keep_id = ids_with_urls[0]  # Keep first one with URL
        else:
            # No URLs, keep the lowest ID
            keep_id = min(ids)

        delete_ids = [x for x in ids if x != keep_id]

        if delete_ids:
            print(f"\n  {year} {make} {model} - ${price:,.0f} @ {mileage:,}mi ({city}, {state})")
            print(f"    Keeping ID {keep_id}, deleting IDs: {delete_ids}")

            # Delete duplicates
            placeholders = ','.join('?' * len(delete_ids))
            cursor.execute(f"""
                DELETE FROM market_prices
                WHERE id IN ({placeholders})
            """, delete_ids)

            deleted = cursor.rowcount
            total_deleted += deleted
            print(f"    → Deleted {deleted} duplicate(s)")

    # Commit changes
    conn.commit()

    # Step 3: Verify results
    print("\n3. Verification...")

    cursor.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT vehicle_id, asking_price, mileage, city, state, COUNT(*) as cnt
            FROM market_prices
            GROUP BY vehicle_id, asking_price, mileage, city, state
            HAVING cnt > 1
        )
    """)

    remaining = cursor.fetchone()[0]

    if remaining > 0:
        print(f"\n⚠ Warning: {remaining} duplicate groups still exist!")
    else:
        print("\n✓ All duplicates removed successfully!")

    # Final summary
    cursor.execute("SELECT COUNT(*) FROM market_prices")
    total_listings = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM market_prices
        WHERE LENGTH(source_url) > 0
    """)
    with_urls = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT vehicle_id) FROM market_prices")
    unique_vehicles = cursor.fetchone()[0]

    print("\n" + "="*80)
    print("DEDUPLICATION COMPLETE")
    print("="*80)
    print(f"Duplicates removed: {total_deleted}")
    print(f"\nFinal Database:")
    print(f"  Total listings: {total_listings}")
    print(f"  With URLs: {with_urls} ({with_urls/total_listings*100:.1f}%)")
    print(f"  Unique vehicles in market: {unique_vehicles}")

    conn.close()


if __name__ == "__main__":
    deduplicate_database()
