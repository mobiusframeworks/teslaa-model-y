#!/usr/bin/env python3
"""
Update Distance Calculations
Recalculate distances for listings missing distance data
"""

import sqlite3
import sys
from geolocation import get_closest_distance


def update_distances(db_path="car_valuation.db"):
    """Update distance calculations for all listings"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("="*80)
    print("UPDATING DISTANCE CALCULATIONS")
    print("="*80)

    # Get all listings
    cursor.execute("""
        SELECT id, city, state, distance_miles
        FROM market_prices
        WHERE city IS NOT NULL AND city != ''
    """)
    listings = cursor.fetchall()

    print(f"\nFound {len(listings)} listings with location data")

    # Calculate distances
    updated = 0
    newly_calculated = 0
    failed = 0
    failed_cities = set()

    for listing_id, city, state, current_distance in listings:
        distance = get_closest_distance(city, state)

        if distance is not None:
            # Update or insert distance
            cursor.execute("""
                UPDATE market_prices
                SET distance_miles = ?
                WHERE id = ?
            """, (distance, listing_id))

            if current_distance is None:
                newly_calculated += 1
            updated += 1
        else:
            failed += 1
            failed_cities.add(f"{city}, {state}")

    conn.commit()

    # Summary
    print(f"\n✓ Updated {updated} listings with distance data")
    print(f"  → Newly calculated: {newly_calculated}")
    print(f"  → Recalculated existing: {updated - newly_calculated}")
    print(f"  → Failed (unknown cities): {failed}")

    if failed_cities:
        print(f"\nCities without coordinates (top 20):")
        for city in sorted(failed_cities)[:20]:
            cursor.execute("""
                SELECT COUNT(*)
                FROM market_prices
                WHERE (city || ', ' || state) = ? AND distance_miles IS NULL
            """, (city,))
            count = cursor.fetchone()[0]
            print(f"  {city}: {count} listing(s)")

    # Final statistics
    cursor.execute("SELECT COUNT(*) FROM market_prices WHERE distance_miles IS NOT NULL")
    total_with_distance = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM market_prices")
    total_listings = cursor.fetchone()[0]

    print("\n" + "="*80)
    print("DISTANCE DATA SUMMARY")
    print("="*80)
    print(f"Total listings: {total_listings}")
    print(f"With distance data: {total_with_distance} ({total_with_distance/total_listings*100:.1f}%)")
    print(f"Missing distance data: {total_listings - total_with_distance}")

    # Show distance distribution
    cursor.execute("""
        SELECT
            CASE
                WHEN distance_miles <= 25 THEN '0-25 miles'
                WHEN distance_miles <= 50 THEN '26-50 miles'
                WHEN distance_miles <= 100 THEN '51-100 miles'
                WHEN distance_miles <= 200 THEN '101-200 miles'
                WHEN distance_miles <= 500 THEN '201-500 miles'
                ELSE '500+ miles'
            END as distance_range,
            COUNT(*) as count
        FROM market_prices
        WHERE distance_miles IS NOT NULL
        GROUP BY distance_range
        ORDER BY MIN(distance_miles)
    """)

    ranges = cursor.fetchall()

    print("\nDistance Distribution:")
    print("-" * 40)
    for distance_range, count in ranges:
        bar = "█" * int(count / 2)
        print(f"{distance_range:15} {count:4} {bar}")

    conn.close()


if __name__ == "__main__":
    update_distances()
