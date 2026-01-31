#!/usr/bin/env python3
"""
Add My Tesla Model Y to Database
Add owner's Tesla listing for market comparison
"""

import sqlite3
from datetime import date
from geolocation import get_closest_distance


def add_my_tesla(db_path="car_valuation.db"):
    """Add my 2024 Tesla Model Y to database"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("="*80)
    print("ADDING YOUR TESLA MODEL Y TO DATABASE")
    print("="*80)

    # Vehicle details
    year = 2024
    make = "Tesla"
    model = "Model Y"
    trim = "Long Range AWD"

    # Listing details
    asking_price = 34900  # Your asking price
    mileage = 46000
    city = "Santa Cruz"
    state = "CA"

    # Get or create vehicle
    cursor.execute("""
        SELECT id FROM vehicles
        WHERE year = ? AND make = ? AND model = ? AND trim = ?
    """, (year, make, model, trim))

    vehicle = cursor.fetchone()

    if vehicle:
        vehicle_id = vehicle[0]
        print(f"\n✓ Vehicle found: {year} {make} {model} {trim} (ID: {vehicle_id})")
    else:
        cursor.execute("""
            INSERT INTO vehicles (year, make, model, trim)
            VALUES (?, ?, ?, ?)
        """, (year, make, model, trim))
        vehicle_id = cursor.lastrowid
        print(f"\n✓ Vehicle created: {year} {make} {model} {trim} (ID: {vehicle_id})")

    # Check if listing already exists
    cursor.execute("""
        SELECT id FROM market_prices
        WHERE vehicle_id = ?
          AND asking_price = ?
          AND mileage = ?
          AND source = 'owner_listing'
    """, (vehicle_id, asking_price, mileage))

    existing = cursor.fetchone()

    if existing:
        print(f"\n⚠ Listing already exists (ID: {existing[0]})")
        print("  Updating listing...")

        cursor.execute("""
            UPDATE market_prices
            SET listing_date = ?
            WHERE id = ?
        """, (date.today().isoformat(), existing[0]))

        listing_id = existing[0]
    else:
        # Calculate distance (should be 0 since you're in Santa Cruz)
        distance = get_closest_distance(city, state)

        # Insert listing
        cursor.execute("""
            INSERT INTO market_prices (
                vehicle_id, asking_price, mileage, city, state,
                source, source_url, distance_miles, listing_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            vehicle_id,
            asking_price,
            mileage,
            city,
            state,
            "owner_listing",
            None,  # Will add Facebook URL once posted
            distance,
            date.today().isoformat()
        ))

        listing_id = cursor.lastrowid
        print(f"\n✓ Listing created (ID: {listing_id})")

    conn.commit()

    # Show comparison with market
    print(f"\n{'='*80}")
    print("MARKET COMPARISON - 2024 Tesla Model Y")
    print(f"{'='*80}")

    cursor.execute("""
        SELECT mp.asking_price, mp.mileage, mp.city, mp.state, mp.source
        FROM market_prices mp
        JOIN vehicles v ON mp.vehicle_id = v.id
        WHERE v.year = 2024 AND v.make = 'Tesla' AND v.model = 'Model Y'
        ORDER BY mp.asking_price DESC
    """)

    listings = cursor.fetchall()

    print(f"\n{'Price':<12} {'Mileage':<12} {'Location':<25} {'Source':<20}")
    print("-" * 80)

    for price, miles, city_name, state_name, source in listings:
        location = f"{city_name}, {state_name}" if city_name else "Unknown"
        is_yours = "← YOUR LISTING" if source == "owner_listing" else ""
        print(f"${price:>10,.0f}  {miles:>10,}mi  {location:<25} {source:<20} {is_yours}")

    print(f"\n{'='*80}")
    print("PRICING ANALYSIS")
    print(f"{'='*80}")

    # Calculate market stats
    market_listings = [p for p, m, c, s, src in listings if src != "owner_listing"]

    if market_listings:
        avg_price = sum(market_listings) / len(market_listings)
        max_price = max(market_listings)
        min_price = min(market_listings)

        print(f"\nMarket Statistics (excluding your listing):")
        print(f"  Average: ${avg_price:,.0f}")
        print(f"  Range: ${min_price:,.0f} - ${max_price:,.0f}")
        print(f"\nYour Listing: ${asking_price:,.0f}")

        diff = asking_price - avg_price
        pct = (diff / avg_price) * 100

        if diff > 0:
            print(f"  ${diff:,.0f} ABOVE average ({pct:+.1f}%)")
        else:
            print(f"  ${abs(diff):,.0f} BELOW average ({pct:+.1f}%)")

        print(f"\n💡 With your upgrades ($3,000+ value), this is a fair price!")

    print(f"\n{'='*80}")
    print("✓ Your Tesla is now in the database!")
    print("✓ View it on the dashboard at http://localhost:8501")
    print("✓ Select 'Tesla Model Y' to see your listing in the regression chart")
    print(f"{'='*80}")

    conn.close()


if __name__ == "__main__":
    add_my_tesla()
