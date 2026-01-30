#!/usr/bin/env python3
"""
Master Scraper Orchestrator
Coordinates all scrapers to build comprehensive pricing database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_scraper import GoogleScraper
from craigslist_scraper import CraigslistScraper
from data_loader import DataLoader
from typing import List, Dict
from datetime import datetime
import json


class MasterScraper:
    """Orchestrate all scrapers"""

    def __init__(self):
        self.google_scraper = GoogleScraper()
        self.craigslist_scraper = CraigslistScraper()
        self.data_loader = DataLoader()

        # Target vehicles from database
        self.target_vehicles = [
            {'make': 'Lexus', 'model': 'GX', 'years': [2024, 2023, 2022, 2021]},
            {'make': 'Ford', 'model': 'F-150', 'years': [2024, 2023, 2022, 2021, 2020]},
            {'make': 'Toyota', 'model': 'Tacoma', 'years': [2024, 2023, 2022, 2021, 2020]},
            {'make': 'Toyota', 'model': 'Tundra', 'years': [2024, 2023, 2022]},
            {'make': 'Toyota', 'model': 'Sequoia', 'years': [2024, 2023, 2022]},
            {'make': 'Tesla', 'model': 'Model Y', 'years': [2024, 2023, 2022, 2021]},
            {'make': 'Tesla', 'model': 'Model 3', 'years': [2024, 2023, 2022, 2021]},
        ]

        # California locations for focused scraping
        self.locations = {
            'bay_area': ['San Francisco', 'Oakland', 'San Jose'],
            'socal': ['Los Angeles', 'San Diego', 'Orange County'],
            'central': ['Sacramento', 'Fresno', 'Bakersfield'],
        }

        # Craigslist region codes
        self.craigslist_regions = [
            'sfbay',
            'sacramento',
            'losangeles',
            'sandiego',
            'orangecounty',
            'inlandempire',
            'fresno',
            'bakersfield',
            'stockton',
            'modesto'
        ]

    def run_full_scrape(self, phase: str = 'all'):
        """
        Run complete scraping operation
        phase: 'google', 'craigslist', 'all'
        """

        print("="*80)
        print("MASTER SCRAPER - Building Price Database Time Capsule".center(80))
        print("="*80)
        print(f"\nStart Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Phase: {phase}")
        print(f"Target Vehicles: {len(self.target_vehicles)}")
        print(f"Regions: {len(self.craigslist_regions)} Craigslist regions")

        results = {
            'start_time': datetime.now().isoformat(),
            'phase': phase,
            'google_results': [],
            'craigslist_results': [],
            'loaded_count': 0
        }

        # Phase 1: Google Search (find listing URLs)
        if phase in ['google', 'all']:
            print(f"\n{'='*80}")
            print("PHASE 1: GOOGLE SEARCH - Finding Listings")
            print('='*80)

            google_vehicles = []
            for vehicle in self.target_vehicles:
                for year in vehicle['years']:
                    google_vehicles.append({
                        'make': vehicle['make'],
                        'model': vehicle['model'],
                        'year': year
                    })

            google_locations = [
                'Bay Area California',
                'Los Angeles California',
                'San Diego California',
                'Sacramento California',
                ''  # Nationwide
            ]

            results['google_results'] = self.google_scraper.scrape_multiple_vehicles(
                google_vehicles,
                google_locations
            )

            print(f"\n✓ Google search complete: {len(results['google_results'])} URLs found")

        # Phase 2: Craigslist Direct Scraping
        if phase in ['craigslist', 'all']:
            print(f"\n{'='*80}")
            print("PHASE 2: CRAIGSLIST - Direct Scraping")
            print('='*80)

            for region in self.craigslist_regions:
                for vehicle in self.target_vehicles:
                    print(f"\nScraping {region}: {vehicle['make']} {vehicle['model']}")

                    # Get listings for this vehicle in this region
                    listings = self.craigslist_scraper.search_region(
                        region=region,
                        make=vehicle['make'],
                        model=vehicle['model'],
                        min_year=min(vehicle['years']),
                        max_results=50
                    )

                    results['craigslist_results'].extend(listings)

                    print(f"  Found {len(listings)} listings")

                    # Polite delay between regions
                    self.craigslist_scraper.random_delay()

            print(f"\n✓ Craigslist scraping complete: {len(results['craigslist_results'])} listings")

        # Phase 3: Load into Database
        print(f"\n{'='*80}")
        print("PHASE 3: LOADING INTO DATABASE")
        print('='*80)

        # Combine and deduplicate results
        all_listings = results['craigslist_results']  # Craigslist has full data

        # Filter out entries without required fields
        valid_listings = [
            l for l in all_listings
            if l.get('price') and l.get('year') and l.get('make') and l.get('model')
        ]

        print(f"\nValid listings to load: {len(valid_listings)}")

        if valid_listings:
            load_stats = self.data_loader.load_listings(valid_listings)
            results['loaded_count'] = load_stats.get('loaded', 0)

            print(f"\n✓ Database loading complete:")
            print(f"  Loaded: {load_stats['loaded']}")
            print(f"  Skipped: {load_stats['skipped']}")
            print(f"  Errors: {load_stats['errors']}")

        # Save master results
        results['end_time'] = datetime.now().isoformat()
        self.save_master_results(results)

        # Print summary
        self.print_summary(results)

    def run_quick_sample(self):
        """Quick sample run for testing (10-15 minutes)"""

        print("="*80)
        print("QUICK SAMPLE SCRAPE".center(80))
        print("="*80)

        # Just 2-3 vehicles, 2-3 regions
        sample_vehicles = [
            {'make': 'Toyota', 'model': 'Tacoma', 'years': [2024, 2023]},
            {'make': 'Lexus', 'model': 'GX', 'years': [2024]},
        ]

        sample_regions = ['sfbay', 'losangeles']

        all_listings = []

        for region in sample_regions:
            for vehicle in sample_vehicles:
                print(f"\nScraping {region}: {vehicle['make']} {vehicle['model']}")

                listings = self.craigslist_scraper.search_region(
                    region=region,
                    make=vehicle['make'],
                    model=vehicle['model'],
                    min_year=min(vehicle['years']),
                    max_results=20
                )

                all_listings.extend(listings)
                self.craigslist_scraper.random_delay()

        print(f"\n✓ Found {len(all_listings)} listings")

        # Load into database
        if all_listings:
            valid_listings = [l for l in all_listings if l.get('price')]
            load_stats = self.data_loader.load_listings(valid_listings)

            print(f"\n✓ Loaded {load_stats['loaded']} listings into database")

    def save_master_results(self, results: Dict):
        """Save master scraping results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = f"scrapers/data/master_scrape_{timestamp}.json"

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n✓ Results saved to: {filepath}")

    def print_summary(self, results: Dict):
        """Print final summary"""

        print(f"\n{'='*80}")
        print("SCRAPING COMPLETE - SUMMARY".center(80))
        print('='*80)

        print(f"\nStart Time: {results['start_time']}")
        print(f"End Time: {results['end_time']}")

        if results.get('google_results'):
            print(f"\nGoogle Search:")
            print(f"  URLs Found: {len(results['google_results'])}")

        if results.get('craigslist_results'):
            print(f"\nCraigslist Scraping:")
            print(f"  Listings Found: {len(results['craigslist_results'])}")

            # Breakdown by vehicle
            by_vehicle = {}
            for listing in results['craigslist_results']:
                key = f"{listing.get('make', 'Unknown')} {listing.get('model', 'Unknown')}"
                by_vehicle[key] = by_vehicle.get(key, 0) + 1

            print(f"\n  By Vehicle:")
            for vehicle, count in sorted(by_vehicle.items(), key=lambda x: x[1], reverse=True):
                print(f"    {vehicle}: {count}")

        print(f"\nDatabase:")
        print(f"  Loaded: {results.get('loaded_count', 0)} listings")

        print(f"\n{'='*80}")
        print("✓ Time Capsule Database Updated!".center(80))
        print('='*80)


def main():
    """Main entry point"""

    import argparse

    parser = argparse.ArgumentParser(description='Master Car Listing Scraper')
    parser.add_argument('--mode', choices=['full', 'quick', 'google', 'craigslist'],
                       default='quick',
                       help='Scraping mode (default: quick)')

    args = parser.parse_args()

    scraper = MasterScraper()

    if args.mode == 'quick':
        print("Running QUICK SAMPLE (10-15 minutes)")
        print("For full scrape, use: --mode full")
        print()
        scraper.run_quick_sample()

    elif args.mode == 'full':
        print("Running FULL SCRAPE (1-2 hours)")
        print("This will scrape all vehicles across all regions")
        print()

        confirm = input("Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            scraper.run_full_scrape(phase='all')
        else:
            print("Cancelled")

    elif args.mode in ['google', 'craigslist']:
        scraper.run_full_scrape(phase=args.mode)


if __name__ == "__main__":
    main()
