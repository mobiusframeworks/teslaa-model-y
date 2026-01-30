#!/usr/bin/env python3
"""
Geolocation and Distance Calculation
Calculate distances between locations for filtering nearby listings
"""

import math
from typing import Tuple, Optional, Dict
import sqlite3


# Reference locations
REFERENCE_LOCATIONS = {
    'Santa Cruz, CA': (36.9741, -122.0308),
    'San Jose, CA': (37.3382, -121.8863),
}


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points in miles using Haversine formula

    Args:
        lat1, lon1: First location coordinates
        lat2, lon2: Second location coordinates

    Returns:
        Distance in miles
    """
    # Earth radius in miles
    R = 3959.0

    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    # Haversine formula
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    return R * c


def get_city_coordinates(city: str, state: str) -> Optional[Tuple[float, float]]:
    """
    Get approximate coordinates for a city

    Returns:
        (latitude, longitude) or None if not found
    """
    # Common California cities
    california_cities = {
        'San Francisco': (37.7749, -122.4194),
        'Oakland': (37.8044, -122.2712),
        'Berkeley': (37.8715, -122.2730),
        'San Jose': (37.3382, -121.8863),
        'Fremont': (37.5485, -121.9886),
        'Santa Cruz': (36.9741, -122.0308),
        'Sacramento': (38.5816, -121.4944),
        'Fresno': (36.7378, -119.7871),
        'Bakersfield': (35.3733, -119.0187),
        'Los Angeles': (34.0522, -118.2437),
        'San Diego': (32.7157, -117.1611),
        'Orange': (33.7879, -117.8531),
        'Irvine': (33.6846, -117.8265),
        'Anaheim': (33.8366, -117.9143),
        'Riverside': (33.9806, -117.3755),
        'Perris': (33.7825, -117.2287),
        'Salinas': (36.6777, -121.6555),
        'San Leandro': (37.7249, -122.1561),
        'Carson': (33.8317, -118.2820),
        'Stockton': (37.9577, -121.2908),
        'Modesto': (37.6391, -120.9969),
        'Walnut Creek': (37.9101, -122.0652),
        'Palo Alto': (37.4419, -122.1430),
        'Cupertino': (37.3230, -122.0322),
        'Mountain View': (37.3861, -122.0839),
        'Sunnyvale': (37.3688, -122.0363),
        'Milpitas': (37.4323, -121.8996),
        'Hayward': (37.6688, -122.0808),
        'San Mateo': (37.5630, -122.3255),
        'Redwood City': (37.4852, -122.2364),
        'Folsom': (38.6779, -121.1760),
        'Roseville': (38.7521, -121.2880),
        'Rocklin': (38.7907, -121.2358),
        'Citrus Heights': (38.7071, -121.2811),
        'Malibu': (34.0259, -118.7798),
        'Pomona': (34.0551, -117.7499),
        'Hesperia': (34.4264, -117.3009),
        'Palmdale': (34.5794, -118.1165),
        'Fontana': (34.0922, -117.4350),
        'San Rafael': (37.9735, -122.5311),
        'Selma': (36.5707, -119.6120),
        'Hanford': (36.3274, -119.6457),
        'Sun Valley': (34.2197, -118.3645),
        'Covina': (34.0900, -117.8903),
        'La Habra': (33.9319, -117.9462),
        'Exeter': (36.2960, -119.1420),
        'Imperial': (32.8473, -115.5694),
        'Fresno': (36.7378, -119.7871),
        'Pacoima': (34.2605, -118.4300),
        'Hollister': (36.8524, -121.4016),
        'Antioch': (38.0049, -121.8058),
        'Oroville': (39.5138, -121.5564),
        'Pleasant Grove': (38.8082, -121.5222),
        'Rancho Cordova': (38.5891, -121.3028),
        'Brentwood': (37.9318, -121.6958),
        'Windsor': (38.5471, -122.8164),
        'Camp Pendleton Marine Corps Base': (33.3142, -117.3150),
        'Highland': (34.1283, -117.2086),
        'Chino Hills': (33.9898, -117.7323),
        'West Sacramento': (38.5805, -121.5302),
        'South Gate': (33.9550, -118.2120),
        'North Hollywood': (34.1878, -118.3792),
        'Ukiah': (39.1502, -123.2078),
        'Perris': (33.7825, -117.2287),
    }

    # Nevada cities
    nevada_cities = {
        'Las Vegas': (36.1699, -115.1398),
        'Reno': (39.5296, -119.8138),
    }

    # Washington cities
    washington_cities = {
        'Seattle': (47.6062, -122.3321),
        'Tacoma': (47.2529, -122.4443),
        'Spokane': (47.6588, -117.4260),
        'Bellevue': (47.6101, -122.2015),
        'Kent': (47.3809, -122.2348),
        'Kirkland': (47.6769, -122.2060),
        'Renton': (47.4829, -122.2171),
        'Bremerton': (47.5673, -122.6326),
        'Fife': (47.2393, -122.3571),
        'Bothell': (47.7623, -122.2054),
        'Auburn': (47.3073, -122.2285),
        'Puyallup': (47.1856, -122.2931),
        'Olympia': (47.0379, -122.9007),
        'Vancouver': (45.6387, -122.6615),
        'Ridgefield': (45.8151, -122.7445),
        'Battle Ground': (45.7809, -122.5354),
        'Lake Oswego': (45.4207, -122.6706),
        'Covington': (47.3581, -122.1215),
        'Monroe': (47.8556, -121.9709),
        'Pullman': (46.7312, -117.1796),
        'Moses Lake': (47.1301, -119.2781),
        'Sumner': (47.2037, -122.2407),
    }

    # Oregon cities
    oregon_cities = {
        'Portland': (45.5152, -122.6784),
        'Eugene': (44.0521, -123.0868),
        'Salem': (44.9429, -123.0351),
        'Bend': (44.0582, -121.3153),
        'Medford': (42.3265, -122.8756),
        'Corvallis': (44.5646, -123.2620),
        'Springfield': (44.0462, -122.9814),
        'Hillsboro': (45.5229, -122.9897),
        'Lebanon': (44.5365, -122.9070),
        'Happy Valley': (45.4470, -122.5195),
        'Warrenton': (46.1651, -123.9237),
        'Hermiston': (45.8404, -119.2894),
        'Umpqua': (43.3165, -123.4551),
        'Coeur D\'Alene': (47.6777, -116.7805),  # Actually Idaho but near OR border
    }

    # Idaho cities
    idaho_cities = {
        'Boise': (43.6150, -116.2023),
        'Meridian': (43.6121, -116.3915),
        'Nampa': (43.5407, -116.5635),
        'Idaho Falls': (43.4666, -112.0341),
        'Pocatello': (42.8713, -112.4455),
        'Caldwell': (43.6629, -116.6874),
        'Coeur D\'Alene': (47.6777, -116.7805),
        'Twin Falls': (42.5630, -114.4608),
        'Eagle': (43.6955, -116.3540),
        'Rathdrum': (47.8119, -116.8976),
        'Huston': (43.6240, -116.3470),
    }

    # Arizona cities
    arizona_cities = {
        'Phoenix': (33.4484, -112.0740),
        'Tucson': (32.2226, -110.9747),
        'Mesa': (33.4152, -111.8315),
        'Chandler': (33.3062, -111.8413),
        'Scottsdale': (33.4942, -111.9261),
        'Glendale': (33.5387, -112.1860),
        'Gilbert': (33.3528, -111.7890),
        'Tempe': (33.4255, -111.9400),
        'Peoria': (33.5806, -112.2374),
        'Surprise': (33.6303, -112.3679),
    }

    # Utah cities
    utah_cities = {
        'Salt Lake City': (40.7608, -111.8910),
        'Provo': (40.2338, -111.6585),
        'West Valley City': (40.6916, -112.0011),
        'West Jordan': (40.6097, -111.9391),
        'Orem': (40.2969, -111.6946),
        'Sandy': (40.5649, -111.8389),
        'Hurricane': (37.1753, -113.2899),
    }

    # Normalize city name
    city_normalized = city.strip()

    if state == 'CA':
        coords = california_cities.get(city_normalized)
    elif state == 'WA':
        coords = washington_cities.get(city_normalized)
    elif state == 'OR':
        coords = oregon_cities.get(city_normalized)
    elif state == 'ID':
        coords = idaho_cities.get(city_normalized)
    elif state == 'AZ':
        coords = arizona_cities.get(city_normalized)
    elif state == 'NV':
        coords = nevada_cities.get(city_normalized)
    elif state == 'UT':
        coords = utah_cities.get(city_normalized)
    else:
        coords = None

    return coords


def calculate_distance_from_reference(city: str, state: str, reference: str = 'Santa Cruz, CA') -> Optional[float]:
    """
    Calculate distance from a reference location

    Args:
        city: City name
        state: State code
        reference: Reference location (default: Santa Cruz, CA)

    Returns:
        Distance in miles or None if coordinates not found
    """
    # Get listing coordinates
    listing_coords = get_city_coordinates(city, state)
    if not listing_coords:
        return None

    # Get reference coordinates
    ref_coords = REFERENCE_LOCATIONS.get(reference)
    if not ref_coords:
        return None

    return haversine_distance(ref_coords[0], ref_coords[1], listing_coords[0], listing_coords[1])


def get_closest_distance(city: str, state: str) -> Optional[float]:
    """
    Get distance to closest reference location (Santa Cruz or San Jose)

    Returns:
        Minimum distance in miles or None
    """
    distances = []

    for ref_location in REFERENCE_LOCATIONS.keys():
        dist = calculate_distance_from_reference(city, state, ref_location)
        if dist is not None:
            distances.append(dist)

    return min(distances) if distances else None


def add_distance_column_to_db(db_path: str = "car_valuation.db"):
    """
    Add distance_miles column to market_prices table and calculate distances
    """
    from database import DatabaseManager

    db = DatabaseManager(db_path)

    with db.get_connection() as conn:
        # Check if column exists
        cursor = conn.execute("PRAGMA table_info(market_prices)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'distance_miles' not in columns:
            print("Adding distance_miles column...")
            conn.execute("ALTER TABLE market_prices ADD COLUMN distance_miles REAL")

        # Calculate distances for all listings
        print("\nCalculating distances from Santa Cruz / San Jose...")
        cursor = conn.execute("SELECT id, city, state FROM market_prices")
        listings = cursor.fetchall()

        updated = 0
        for listing_id, city, state in listings:
            if city and state:
                distance = get_closest_distance(city, state)
                if distance is not None:
                    conn.execute("UPDATE market_prices SET distance_miles = ? WHERE id = ?",
                               (distance, listing_id))
                    updated += 1

        print(f"\n✓ Updated {updated} listings with distance calculations")


def main():
    """Test distance calculations"""

    print("="*80)
    print("DISTANCE CALCULATION TEST")
    print("="*80)

    # Test cities
    test_cities = [
        ("Santa Cruz", "CA"),
        ("San Jose", "CA"),
        ("San Francisco", "CA"),
        ("Los Angeles", "CA"),
        ("Sacramento", "CA"),
        ("Las Vegas", "NV"),
    ]

    print("\nDistances from Santa Cruz, CA:")
    print("-" * 50)
    for city, state in test_cities:
        dist = calculate_distance_from_reference(city, state, "Santa Cruz, CA")
        if dist:
            print(f"{city}, {state}: {dist:.1f} miles")

    print("\nDistances from San Jose, CA:")
    print("-" * 50)
    for city, state in test_cities:
        dist = calculate_distance_from_reference(city, state, "San Jose, CA")
        if dist:
            print(f"{city}, {state}: {dist:.1f} miles")

    print("\nClosest distance (Santa Cruz OR San Jose):")
    print("-" * 50)
    for city, state in test_cities:
        dist = get_closest_distance(city, state)
        if dist:
            print(f"{city}, {state}: {dist:.1f} miles")


if __name__ == "__main__":
    main()
