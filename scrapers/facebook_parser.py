"""
Facebook Marketplace Parser
Parse copied Facebook Marketplace listings into database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager, Vehicle, MarketPrice, VehicleRepository, MarketPriceRepository
import re
from datetime import datetime
from typing import List, Dict, Optional
import subprocess

# Import geolocation if available
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from geolocation import get_closest_distance
    GEOLOCATION_AVAILABLE = True
except ImportError:
    GEOLOCATION_AVAILABLE = False
    get_closest_distance = None


class FacebookParser:
    """Parse Facebook Marketplace text data"""

    def __init__(self):
        # Use database in parent directory
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "car_valuation.db")
        self.db = DatabaseManager(db_path)
        self.vehicle_repo = VehicleRepository(self.db)
        self.price_repo = MarketPriceRepository(self.db)

    def extract_urls_from_rtf(self, rtf_filepath: str) -> List[str]:
        """Extract Facebook Marketplace URLs from RTF file"""
        urls = []

        try:
            with open(rtf_filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Find all HYPERLINK patterns
            pattern = r'\{\\field\{\\\*\\fldinst\{HYPERLINK "([^"]+)"\}\}'
            matches = re.findall(pattern, content)

            # Filter for marketplace item URLs only
            for url in matches:
                if 'facebook.com/marketplace/item/' in url:
                    # Clean up the URL
                    clean_url = url.split('?')[0] if '?' in url else url
                    urls.append(url)  # Keep full URL with tracking params

        except Exception as e:
            print(f"Error extracting URLs from RTF: {e}")

        return urls

    def parse_facebook_text(self, filepath: str, min_price: int = 3000, max_price: int = 50000) -> List[Dict]:
        """Parse Facebook Marketplace text file with price filtering"""

        # Check if this is an RTF file path (original) or text file
        rtf_filepath = None
        if filepath.endswith('.txt'):
            # Try to find original RTF file
            potential_rtf = filepath.replace('/tmp/', '/Users/macmini/Desktop/').replace('_scrape.txt', ' scrape 1:30.rtfd/TXT.rtf')
            if os.path.exists(potential_rtf):
                rtf_filepath = potential_rtf
        elif filepath.endswith('.rtf'):
            rtf_filepath = filepath

        # Extract URLs if RTF file is available
        urls = []
        if rtf_filepath:
            print(f"Extracting URLs from: {rtf_filepath}")
            urls = self.extract_urls_from_rtf(rtf_filepath)
            print(f"Found {len(urls)} listing URLs")

        with open(filepath, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        listings = []
        filtered_count = 0
        url_index = 0
        i = 0

        while i < len(lines):
            line = lines[i]

            # Look for price pattern
            if line.startswith('$') and ',' in line:
                try:
                    listing = self.parse_listing_block(lines, i, min_price, max_price)
                    if listing:
                        # Attach URL if available
                        if url_index < len(urls):
                            listing['source_url'] = urls[url_index]
                            url_index += 1

                        listings.append(listing)
                        url_status = "with URL" if listing.get('source_url') else "no URL"
                        print(f"Parsed: {listing.get('year')} {listing.get('make')} {listing.get('model')} - ${listing.get('price'):,} ({url_status})")
                    else:
                        # Check if it was filtered by price
                        price_check = self.extract_price(line)
                        if price_check and (price_check < min_price or price_check > max_price):
                            filtered_count += 1
                            # Still increment URL index for filtered listings
                            if url_index < len(urls):
                                url_index += 1
                except Exception as e:
                    print(f"Error parsing listing at line {i}: {e}")

            i += 1

        if filtered_count > 0:
            print(f"\n⊗ Filtered out {filtered_count} listings (price < ${min_price:,} or > ${max_price:,})")

        return listings

    def parse_listing_block(self, lines: List[str], start_idx: int, min_price: int = 3000, max_price: int = 50000) -> Optional[Dict]:
        """Parse a single listing block with price filtering"""

        # Line 0: Price
        price_line = lines[start_idx]
        price = self.extract_price(price_line)
        if not price:
            return None

        # Filter out fake low prices (down payments) and listings over max
        if price < min_price or price > max_price:
            return None

        # Line 1: Usually year + make + model
        if start_idx + 1 >= len(lines):
            return None

        title_line = lines[start_idx + 1]

        # Extract year, make, model
        year = self.extract_year(title_line)
        make, model = self.extract_make_model(title_line)

        if not (year and make and model):
            return None

        # Line 2: Usually location
        location_line = lines[start_idx + 2] if start_idx + 2 < len(lines) else ""
        city, state = self.extract_location(location_line)

        # Line 3: Often mileage
        mileage_line = lines[start_idx + 3] if start_idx + 3 < len(lines) else ""
        mileage = self.extract_mileage(mileage_line)

        return {
            'price': price,
            'year': year,
            'make': make,
            'model': model,
            'city': city,
            'state': state,
            'mileage': mileage if mileage else 0,
            'source': 'facebook_marketplace',
            'listing_date': datetime.now().strftime('%Y-%m-%d')
        }

    def extract_price(self, text: str) -> Optional[float]:
        """Extract price from text"""
        # Remove $ and commas
        text = text.replace('$', '').replace(',', '').strip()

        match = re.search(r'(\d+)', text)
        if match:
            try:
                price = float(match.group(1))
                if 1000 <= price <= 500000:
                    return price
            except ValueError:
                pass
        return None

    def extract_year(self, text: str) -> Optional[int]:
        """Extract year from text"""
        # Look for 4-digit year
        match = re.search(r'\b(19\d{2}|20\d{2})\b', text)
        if match:
            year = int(match.group(1))
            if 1990 <= year <= 2026:
                return year
        return None

    def extract_make_model(self, text: str) -> tuple:
        """Extract make and model from text with normalized capitalization"""
        text = text.lower()

        # Known makes and their common models
        makes_models = {
            'lexus': {
                'models': ['gx', 'lx', 'rx', 'nx', 'es', 'is', 'gs', 'rc', 'ls'],
                'full_names': {
                    'gx 460': 'GX',
                    'gx 550': 'GX',
                    'lx 570': 'LX',
                    'lx 600': 'LX',
                    'rx 350': 'RX',
                    'rx 400h': 'RX',
                    'es 350': 'ES',
                    'is 350': 'IS',
                    'gs 350': 'GS',
                    'gs f': 'GS',
                    'rc 350': 'RC',
                    'ls 500': 'LS',
                    'nx 350': 'NX'
                }
            },
            'toyota': {
                'models': ['tacoma', 'tundra', 'sequoia', '4runner', 'highlander', 'camry', 'corolla', 'hilux'],
                'full_names': {
                    'hilux surf': 'Hilux',
                    'hilux': 'Hilux'
                }
            },
            'ford': {
                'models': ['f-150', 'f150', 'f-250', 'f250', 'explorer', 'expedition'],
                'full_names': {
                    'f-150': 'F-150',
                    'f150': 'F-150',
                    'f-250': 'F-250',
                    'f250': 'F-250'
                }
            },
            'tesla': {
                'models': ['model y', 'model 3', 'model s', 'model x'],
                'full_names': {
                    'model y': 'Model Y',
                    'model 3': 'Model 3',
                    'model s': 'Model S',
                    'model x': 'Model X'
                }
            },
            'chevrolet': {
                'models': ['silverado', 'tahoe', 'suburban'],
                'full_names': {}
            },
            'gmc': {
                'models': ['sierra', 'yukon'],
                'full_names': {}
            }
        }

        # Find make
        for make, info in makes_models.items():
            if make in text:
                # Check full names first (e.g., "gx 460" -> "GX")
                for full_name, short_model in info['full_names'].items():
                    if full_name in text:
                        return make.title(), short_model

                # Check simple models
                for model in info['models']:
                    if model in text:
                        # Normalize capitalization by make
                        if make == 'lexus':
                            # Lexus: all uppercase (GX, RX, ES, etc.)
                            return 'Lexus', model.upper()
                        elif make == 'tesla':
                            # Tesla: Model X format
                            if model.startswith('model '):
                                return 'Tesla', 'Model ' + model[-1].upper()
                            return 'Tesla', model.title()
                        else:
                            # Others: Title Case
                            return make.title(), model.title()

        return '', ''

    def extract_location(self, text: str) -> tuple:
        """Extract city and state"""
        # Look for pattern: "City, ST"
        match = re.search(r'([^,]+),\s*([A-Z]{2})', text)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return '', ''

    def extract_mileage(self, text: str) -> Optional[int]:
        """Extract mileage"""
        # Look for pattern like "118K miles" or "60K miles"
        match = re.search(r'(\d+)K?\s*miles', text, re.IGNORECASE)
        if match:
            num = int(match.group(1))
            # If it's like "118" and has K, multiply by 1000
            if 'k' in text.lower():
                return num * 1000
            return num
        return None

    def load_to_database(self, listings: List[Dict], deduplicate: bool = True) -> Dict:
        """Load parsed listings into database with deduplication"""

        stats = {
            'total': len(listings),
            'loaded': 0,
            'skipped': 0,
            'duplicates': 0,
            'errors': 0
        }

        # Deduplicate by price + mileage combination
        if deduplicate:
            unique_listings = []
            seen = set()

            for listing in listings:
                # Create unique key from price, mileage, make, model, year
                key = (
                    listing.get('price'),
                    listing.get('mileage', 0),
                    listing.get('make'),
                    listing.get('model'),
                    listing.get('year')
                )

                if key not in seen:
                    seen.add(key)
                    unique_listings.append(listing)
                else:
                    stats['duplicates'] += 1
                    print(f"⊗ Duplicate skipped: {listing['year']} {listing['make']} {listing['model']} - ${listing['price']:,} @ {listing.get('mileage', 0)} mi")

            listings = unique_listings
            print(f"\n✓ Removed {stats['duplicates']} duplicates, {len(listings)} unique listings remain")

        # Also check against existing database entries
        for listing in listings:
            try:
                # Get or create vehicle
                vehicle_id = self.get_or_create_vehicle(listing)
                if not vehicle_id:
                    stats['skipped'] += 1
                    continue

                # Check if this exact listing already exists in database
                if self.listing_exists(vehicle_id, listing['price'], listing.get('mileage', 0)):
                    stats['duplicates'] += 1
                    print(f"⊗ Already in DB: {listing['year']} {listing['make']} {listing['model']} - ${listing['price']:,}")
                    continue

                # Determine region
                region = self.determine_region(listing.get('city', ''), listing.get('state', ''))

                # Calculate distance if geolocation available
                distance = None
                if GEOLOCATION_AVAILABLE and listing.get('city') and listing.get('state'):
                    distance = get_closest_distance(listing['city'], listing['state'])

                # Create market listing
                market_listing = MarketPrice(
                    vehicle_id=vehicle_id,
                    listing_date=listing.get('listing_date', datetime.now().strftime('%Y-%m-%d')),
                    mileage=listing.get('mileage', 0),
                    asking_price=listing['price'],
                    condition='good',  # Default, adjust if needed
                    city=listing.get('city', ''),
                    state=listing.get('state', 'CA'),
                    region=region,
                    source='facebook_marketplace',
                    source_url=listing.get('source_url', '')
                )

                listing_id = self.price_repo.add_listing(market_listing)

                # Update distance if calculated
                if distance is not None:
                    with self.db.get_connection() as conn:
                        conn.execute("UPDATE market_prices SET distance_miles = ? WHERE id = ?",
                                   (distance, listing_id))
                stats['loaded'] += 1

                print(f"✓ Loaded: {listing['year']} {listing['make']} {listing['model']} - ${listing['price']:,} (ID: {listing_id})")

            except Exception as e:
                print(f"✗ Error loading: {e}")
                stats['errors'] += 1

        return stats

    def get_or_create_vehicle(self, listing: Dict) -> Optional[int]:
        """Get existing vehicle or create new one"""

        # Try to find existing
        vehicles = self.vehicle_repo.find_vehicles(
            make=listing['make'],
            model=listing['model'],
            year_min=listing['year'],
            year_max=listing['year']
        )

        if vehicles:
            return vehicles[0]['id']

        # Create new vehicle
        vehicle = Vehicle(
            make=listing['make'],
            model=listing['model'],
            year=listing['year'],
            trim='',
            fuel_type='gasoline'
        )

        vehicle_id = self.vehicle_repo.create_vehicle(vehicle)
        print(f"  Created vehicle: {vehicle.year} {vehicle.make} {vehicle.model}")

        return vehicle_id

    def listing_exists(self, vehicle_id: int, price: float, mileage: int) -> bool:
        """Check if listing with same price and mileage already exists"""

        query = """
            SELECT COUNT(*) as count
            FROM market_prices
            WHERE vehicle_id = ?
              AND asking_price = ?
              AND mileage = ?
        """

        with self.db.get_connection() as conn:
            cursor = conn.execute(query, (vehicle_id, price, mileage))
            result = cursor.fetchone()
            return result[0] > 0 if result else False

    def determine_region(self, city: str, state: str) -> str:
        """Determine region from city/state"""

        if state == 'CA':
            city_lower = city.lower()

            # Bay Area
            bay_cities = ['san francisco', 'oakland', 'berkeley', 'san jose', 'fremont']
            if any(c in city_lower for c in bay_cities):
                return 'Bay Area'

            # SoCal
            socal_cities = ['los angeles', 'san diego', 'orange', 'irvine']
            if any(c in city_lower for c in socal_cities):
                return 'SoCal'

            # Central Valley
            central_cities = ['sacramento', 'fresno', 'bakersfield']
            if any(c in city_lower for c in central_cities):
                return 'Central Valley'

            return 'Other CA'

        # Out of state
        state_regions = {
            'WA': 'Washington',
            'OR': 'Oregon',
            'NV': 'Nevada',
            'AZ': 'Arizona',
            'ID': 'Idaho'
        }

        return state_regions.get(state, 'Out of State')


def main():
    """Import Facebook Marketplace data"""

    parser = FacebookParser()

    filepath = "/tmp/fb_scrape.txt"

    print("="*80)
    print("FACEBOOK MARKETPLACE IMPORT")
    print("="*80)

    # Parse the file
    print(f"\nParsing: {filepath}")
    listings = parser.parse_facebook_text(filepath)

    print(f"\n✓ Parsed {len(listings)} listings")

    # Show summary
    makes = {}
    for listing in listings:
        make = listing.get('make', 'Unknown')
        makes[make] = makes.get(make, 0) + 1

    print("\nBy Make:")
    for make, count in sorted(makes.items(), key=lambda x: x[1], reverse=True):
        print(f"  {make}: {count}")

    # Load to database
    print(f"\n{'='*80}")
    print("LOADING TO DATABASE")
    print('='*80)

    stats = parser.load_to_database(listings)

    print(f"\n{'='*80}")
    print("IMPORT COMPLETE")
    print('='*80)
    print(f"Total Parsed: {stats['total']}")
    print(f"Loaded: {stats['loaded']}")
    print(f"Duplicates Removed: {stats['duplicates']}")
    print(f"Skipped: {stats['skipped']}")
    print(f"Errors: {stats['errors']}")

    if stats['loaded'] > 0:
        print(f"\n✓ Successfully imported {stats['loaded']} NEW listings!")
        print("\nView in dashboard: http://localhost:8501")
        print("Or CLI: python3 car_finder.py -> [3] View All Listings")


if __name__ == "__main__":
    main()
