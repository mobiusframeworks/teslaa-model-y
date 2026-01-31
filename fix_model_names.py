#!/usr/bin/env python3
"""
Fix Model Name Normalization
Consolidate split model names (e.g., "GX 460" -> "GX")
"""

import sqlite3


def fix_model_names(db_path="car_valuation.db"):
    """Normalize model names"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("="*80)
    print("FIXING MODEL NAMES")
    print("="*80)

    # Get all Lexus GX variations
    cursor.execute("""
        SELECT DISTINCT model, COUNT(*) as count
        FROM vehicles
        WHERE make = 'Lexus' AND model LIKE '%GX%'
        GROUP BY model
        ORDER BY model
    """)

    gx_models = cursor.fetchall()

    print("\nLexus GX variations found:")
    for model, count in gx_models:
        print(f"  {model}: {count} entries")

    # First, find what the canonical vehicles would be (year, make='Lexus', model='GX')
    print("\nFinding canonical GX vehicles for each year...")

    # Get all years that have GX
    cursor.execute("""
        SELECT DISTINCT year
        FROM vehicles
        WHERE make = 'Lexus' AND model LIKE '%GX%'
        ORDER BY year
    """)

    years = [row[0] for row in cursor.fetchall()]

    print(f"  Found {len(years)} distinct years")

    # For each year, merge all GX variations
    print("\nMerging GX variations...")

    for year in years:
        # Get all vehicle IDs for this year with GX variations
        cursor.execute("""
            SELECT id, model
            FROM vehicles
            WHERE make = 'Lexus' AND model LIKE '%GX%' AND year = ?
            ORDER BY CASE
                WHEN model = 'GX' THEN 0
                ELSE 1
            END, id
        """, (year,))

        vehicles = cursor.fetchall()

        if len(vehicles) <= 1:
            continue

        # First one is canonical (prefer 'GX' if it exists, otherwise lowest ID)
        canonical_id, canonical_model = vehicles[0]
        duplicate_ids = [v[0] for v in vehicles[1:]]

        print(f"\n  {year} Lexus GX:")
        print(f"    Canonical: ID {canonical_id} (model='{canonical_model}')")
        print(f"    Merging: {[f"ID {vid} ({vmodel})" for vid, vmodel in vehicles[1:]]}")

        # Move all market_prices to canonical vehicle
        for dup_id in duplicate_ids:
            cursor.execute("""
                UPDATE market_prices
                SET vehicle_id = ?
                WHERE vehicle_id = ?
            """, (canonical_id, dup_id))

            moved = cursor.rowcount
            if moved > 0:
                print(f"      → Moved {moved} listings to canonical")

        # Delete duplicate vehicle entries
        placeholders = ','.join('?' * len(duplicate_ids))
        cursor.execute(f"""
            DELETE FROM vehicles
            WHERE id IN ({placeholders})
        """, duplicate_ids)

        deleted = cursor.rowcount
        print(f"      → Deleted {deleted} duplicate vehicle(s)")

        # Now update canonical to just 'GX' if it isn't already
        if canonical_model != 'GX':
            cursor.execute("""
                UPDATE vehicles
                SET model = 'GX'
                WHERE id = ?
            """, (canonical_id,))
            print(f"      → Updated canonical to model='GX'")

    # Check for any remaining duplicates
    print("\nChecking for remaining duplicates...")

    cursor.execute("""
        SELECT year, make, model, COUNT(*) as count, GROUP_CONCAT(id) as ids
        FROM vehicles
        WHERE make = 'Lexus' AND model = 'GX'
        GROUP BY year, make, model
        HAVING count > 1
    """)

    duplicates = cursor.fetchall()

    if duplicates:
        print(f"Found {len(duplicates)} duplicate groups")

        for year, make, model, count, ids_str in duplicates:
            ids = [int(x) for x in ids_str.split(',')]
            keep_id = min(ids)
            delete_ids = [x for x in ids if x != keep_id]

            print(f"\n  {year} {make} {model}:")
            print(f"    Keeping ID {keep_id}, merging {delete_ids}")

            # Update market_prices to point to canonical vehicle
            for dup_id in delete_ids:
                cursor.execute("""
                    UPDATE market_prices
                    SET vehicle_id = ?
                    WHERE vehicle_id = ?
                """, (keep_id, dup_id))

                moved = cursor.rowcount
                if moved > 0:
                    print(f"      → Moved {moved} listings from ID {dup_id} to {keep_id}")

            # Delete duplicate vehicle entries
            placeholders = ','.join('?' * len(delete_ids))
            cursor.execute(f"""
                DELETE FROM vehicles
                WHERE id IN ({placeholders})
            """, delete_ids)

            deleted = cursor.rowcount
            print(f"      → Deleted {deleted} duplicate vehicle(s)")

    conn.commit()

    # Verify results
    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80)

    cursor.execute("""
        SELECT DISTINCT v.make, v.model, COUNT(*) as count
        FROM market_prices mp
        JOIN vehicles v ON mp.vehicle_id = v.id
        WHERE v.make IN ('Lexus', 'Tesla')
        GROUP BY v.make, v.model
        ORDER BY v.make, v.model
    """)

    models = cursor.fetchall()

    print("\nLexus & Tesla models after fix:")
    for make, model, count in models:
        print(f"  {make} {model}: {count} listings")

    # Total counts
    cursor.execute("SELECT COUNT(*) FROM market_prices")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT vehicle_id) FROM market_prices")
    unique_vehicles = cursor.fetchone()[0]

    print(f"\n{'='*80}")
    print(f"Total listings: {total}")
    print(f"Unique vehicles: {unique_vehicles}")
    print(f"{'='*80}")

    conn.close()


if __name__ == "__main__":
    fix_model_names()
