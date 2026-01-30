"""
Data Loader
Load scraped listings into the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager, VehicleRepository, MarketPriceRepository, MarketPrice
from typing import List, Dict
import json
from datetime import datetime
from glob import glob


class DataLoader:
    """Load scraped data into database"""

    def __init__(self):
        self.db = DatabaseManager()
        self.vehicle_repo = VehicleRepository(self.db)
        self.price_repo = MarketPriceRepository(self.db)

    def load_listings(self, listings: List[Dict]) -> Dict:
        """Load listings into database"""

        stats = {
            'total': len(listings),
            'loaded': 0,
            'skipped': 0,
            'errors': 0,
            'new_vehicles': 0
        }

        for listing in listings:
            try:
                # Validate required fields
                if not all([
                    listing.get('make'),
                    listing.get('model'),
                    listing.get('year'),
                    listing.get('price')
                ]):
                    print(f"Skipping listing with missing required fields")
                    stats['skipped'] += 1
                    continue

                # Find or create vehicle
                vehicle_id = self.get_or_create_vehicle(listing)
                if not vehicle_id:
                    print(f"Could not create vehicle for {listing.get('year')} {listing.get('make')} {listing.get('model')}")
                    stats['skipped'] += 1
                    continue

                # Create market price entry
                market_listing = MarketPrice(
                    vehicle_id=vehicle_id,
                    listing_date=listing.get('listing_date', datetime.now().strftime('%Y-%m-%d')),
                    mileage=listing.get('mileage', 0),
                    asking_price=listing['price'],
                    condition=listing.get('condition', 'good'),
                    city=listing.get('city', ''),
                    state=listing.get('state', 'CA'),
                    region=listing.get('region', ''),
                    has_leather=listing.get('has_leather', False),
                    has_tow_package=listing.get('has_tow', False),
                    has_nav=listing.get('has_nav', False),
                    source=listing.get('source', 'scraped'),
                    source_url=listing.get('url', '')
                )

                listing_id = self.price_repo.add_listing(market_listing)
                stats['loaded'] += 1

                print(f"✓ Loaded: {listing['year']} {listing['make']} {listing['model']} - ${listing['price']:,} (ID: {listing_id})")

            except Exception as e:
                print(f"✗ Error loading listing: {e}")
                stats['errors'] += 1

        return stats

    def get_or_create_vehicle(self, listing: Dict) -> int:
        """Get existing vehicle or create basic entry"""

        # Try to find existing
        vehicles = self.vehicle_repo.find_vehicles(
            make=listing['make'],
            model=listing['model'],
            year_min=listing['year'],
            year_max=listing['year']
        )

        if vehicles:
            return vehicles[0]['id']

        # Create basic vehicle entry
        from database import Vehicle

        vehicle = Vehicle(
            make=listing['make'],
            model=listing['model'],
            year=listing['year'],
            trim=listing.get('trim', ''),
            drivetrain=listing.get('drivetrain', ''),
            fuel_type=listing.get('fuel_type', 'gasoline'),
            transmission=listing.get('transmission', ''),
            msrp=listing.get('msrp', 0)
        )

        vehicle_id = self.vehicle_repo.create_vehicle(vehicle)
        print(f"  Created new vehicle: {vehicle.year} {vehicle.make} {vehicle.model} (ID: {vehicle_id})")

        return vehicle_id

    def load_from_json(self, filepath: str) -> Dict:
        """Load listings from JSON file"""

        print(f"\nLoading data from: {filepath}")

        with open(filepath, 'r') as f:
            data = json.load(f)

        if isinstance(data, dict) and 'listings' in data:
            listings = data['listings']
        elif isinstance(data, list):
            listings = data
        else:
            print("Unknown data format")
            return {'error': 'Unknown format'}

        return self.load_listings(listings)

    def load_all_scraped_data(self, data_dir: str = "scrapers/data") -> Dict:
        """Load all JSON files from data directory"""

        json_files = glob(f"{data_dir}/*.json")

        if not json_files:
            print(f"No JSON files found in {data_dir}")
            return {'error': 'No files found'}

        print(f"Found {len(json_files)} JSON files to load")

        total_stats = {
            'files_processed': 0,
            'total_listings': 0,
            'total_loaded': 0,
            'total_skipped': 0,
            'total_errors': 0
        }

        for json_file in json_files:
            print(f"\n{'='*60}")
            print(f"Processing: {json_file}")
            print('='*60)

            stats = self.load_from_json(json_file)

            total_stats['files_processed'] += 1
            total_stats['total_listings'] += stats.get('total', 0)
            total_stats['total_loaded'] += stats.get('loaded', 0)
            total_stats['total_skipped'] += stats.get('skipped', 0)
            total_stats['total_errors'] += stats.get('errors', 0)

        return total_stats


def main():
    """Demo: Load scraped data"""

    loader = DataLoader()

    print("="*60)
    print("DATA LOADER - Loading Scraped Listings")
    print("="*60)

    # Load all scraped data
    stats = loader.load_all_scraped_data()

    print(f"\n{'='*60}")
    print("LOADING COMPLETE")
    print('='*60)
    print(f"Files Processed: {stats.get('files_processed', 0)}")
    print(f"Total Listings: {stats.get('total_listings', 0)}")
    print(f"Loaded Successfully: {stats.get('total_loaded', 0)}")
    print(f"Skipped: {stats.get('total_skipped', 0)}")
    print(f"Errors: {stats.get('total_errors', 0)}")

    if stats.get('total_loaded', 0) > 0:
        success_rate = (stats['total_loaded'] / stats['total_listings']) * 100
        print(f"Success Rate: {success_rate:.1f}%")


if __name__ == "__main__":
    main()
