#!/usr/bin/env python3
"""
Normalize Model Capitalization
Fix inconsistent capitalization in vehicle models (e.g., GX vs Gx vs gx)
"""

import sqlite3
import sys


def normalize_database(db_path="car_valuation.db"):
    """Normalize all model names to consistent capitalization"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("="*80)
    print("NORMALIZING MODEL CAPITALIZATION")
    print("="*80)

    # Step 1: Find all variants
    print("\n1. Finding capitalization variants...")

    cursor.execute("""
        SELECT
            make,
            UPPER(model) as normalized_model,
            GROUP_CONCAT(DISTINCT model) as variants,
            COUNT(DISTINCT model) as variant_count
        FROM vehicles
        GROUP BY make, UPPER(model)
        HAVING variant_count > 1
        ORDER BY make, normalized_model
    """)

    variants = cursor.fetchall()

    if not variants:
        print("✓ No capitalization variants found. Database is clean.")
        conn.close()
        return

    print(f"\nFound {len(variants)} models with capitalization variants:")
    for make, normalized, variant_list, count in variants:
        print(f"  {make} {normalized}: {variant_list} ({count} variants)")

    # Step 2: For each variant group, consolidate to one canonical form
    print("\n2. Consolidating vehicles...")

    total_merged = 0
    total_deleted = 0

    for make, normalized_model, variant_list, variant_count in variants:
        # Get all vehicle IDs for this make/normalized_model combination
        cursor.execute("""
            SELECT id, year, model, trim
            FROM vehicles
            WHERE make = ? AND UPPER(model) = ?
            ORDER BY year,
                     CASE
                         WHEN model = UPPER(model) THEN 0  -- Prefer all uppercase
                         WHEN model = ? THEN 1  -- Then title case
                         ELSE 2  -- Then others
                     END,
                     id
        """, (make, normalized_model, normalized_model.title()))

        vehicles = cursor.fetchall()

        # Group by year
        by_year = {}
        for vid, year, model, trim in vehicles:
            if year not in by_year:
                by_year[year] = []
            by_year[year].append((vid, model, trim))

        # For each year, merge duplicates
        for year, year_vehicles in by_year.items():
            if len(year_vehicles) <= 1:
                continue

            # Pick canonical vehicle (first one, which is all uppercase if available)
            canonical_id, canonical_model, canonical_trim = year_vehicles[0]
            duplicate_ids = [vid for vid, _, _ in year_vehicles[1:]]

            if duplicate_ids:
                print(f"\n  {make} {normalized_model} ({year}):")
                print(f"    Canonical: ID {canonical_id} (model='{canonical_model}')")
                print(f"    Duplicates: {duplicate_ids}")

                # Update market_prices to point to canonical vehicle
                for dup_id in duplicate_ids:
                    cursor.execute("""
                        UPDATE market_prices
                        SET vehicle_id = ?
                        WHERE vehicle_id = ?
                    """, (canonical_id, dup_id))

                    rows_updated = cursor.rowcount
                    if rows_updated > 0:
                        print(f"      → Moved {rows_updated} listings from ID {dup_id} to {canonical_id}")
                        total_merged += rows_updated

                # Delete duplicate vehicle entries
                cursor.execute(f"""
                    DELETE FROM vehicles
                    WHERE id IN ({','.join('?' * len(duplicate_ids))})
                """, duplicate_ids)

                deleted = cursor.rowcount
                total_deleted += deleted
                print(f"      → Deleted {deleted} duplicate vehicle entries")

    # Step 3: Normalize remaining models to uppercase (for Lexus) or Title Case (for others)
    print("\n3. Normalizing remaining model names...")

    # Lexus models should be all uppercase
    cursor.execute("""
        UPDATE vehicles
        SET model = UPPER(model)
        WHERE make = 'Lexus' AND model != UPPER(model)
    """)
    lexus_updated = cursor.rowcount
    if lexus_updated > 0:
        print(f"  ✓ Normalized {lexus_updated} Lexus models to uppercase")

    # Toyota models should be Title Case
    cursor.execute("""
        UPDATE vehicles
        SET model = UPPER(SUBSTR(model, 1, 1)) || LOWER(SUBSTR(model, 2))
        WHERE make = 'Toyota' AND model != (UPPER(SUBSTR(model, 1, 1)) || LOWER(SUBSTR(model, 2)))
    """)
    toyota_updated = cursor.rowcount
    if toyota_updated > 0:
        print(f"  ✓ Normalized {toyota_updated} Toyota models to Title Case")

    # Tesla models should be "Model X" format
    cursor.execute("""
        UPDATE vehicles
        SET model = 'Model ' || UPPER(SUBSTR(TRIM(REPLACE(model, 'model', '')), 1, 1))
        WHERE make = 'Tesla'
          AND LOWER(model) LIKE 'model%'
          AND model NOT LIKE 'Model _'
    """)
    tesla_updated = cursor.rowcount
    if tesla_updated > 0:
        print(f"  ✓ Normalized {tesla_updated} Tesla models to 'Model X' format")

    # Commit changes
    conn.commit()

    # Step 4: Verify results
    print("\n4. Verification...")

    cursor.execute("""
        SELECT
            make,
            UPPER(model) as normalized_model,
            COUNT(DISTINCT model) as variant_count,
            GROUP_CONCAT(DISTINCT model) as variants
        FROM vehicles
        GROUP BY make, UPPER(model)
        HAVING variant_count > 1
    """)

    remaining = cursor.fetchall()

    if remaining:
        print(f"\n⚠ Warning: {len(remaining)} models still have variants:")
        for make, normalized, count, variants in remaining:
            print(f"  {make} {normalized}: {variants}")
    else:
        print("\n✓ All models normalized successfully!")

    # Final summary
    cursor.execute("SELECT COUNT(DISTINCT make || model) FROM vehicles")
    unique_models = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM vehicles")
    total_vehicles = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM market_prices")
    total_listings = cursor.fetchone()[0]

    print("\n" + "="*80)
    print("NORMALIZATION COMPLETE")
    print("="*80)
    print(f"Listings consolidated: {total_merged}")
    print(f"Duplicate vehicles deleted: {total_deleted}")
    print(f"Lexus models normalized: {lexus_updated}")
    print(f"Toyota models normalized: {toyota_updated}")
    print(f"Tesla models normalized: {tesla_updated}")
    print(f"\nFinal Database:")
    print(f"  Unique models: {unique_models}")
    print(f"  Vehicle entries: {total_vehicles}")
    print(f"  Market listings: {total_listings}")

    conn.close()


if __name__ == "__main__":
    normalize_database()
