"""
Google Search Scraper
Finds car listings via Google search and extracts links
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_scraper import BaseScraper
from typing import List, Dict
import urllib.parse
import re


class GoogleScraper(BaseScraper):
    """Scrape Google search results for car listings"""

    def __init__(self):
        super().__init__(delay_min=3, delay_max=7)  # Longer delays for Google
        self.base_url = "https://www.google.com/search"

    def build_search_query(self, make: str, model: str, year: int, location: str = "") -> str:
        """Build Google search query for car listings"""
        query_parts = [
            f"{year} {make} {model}",
            "for sale"
        ]

        if location:
            query_parts.append(location)

        # Add common car sites to focus results
        query_parts.append("site:craigslist.org OR site:autotrader.com OR site:cars.com OR site:cargurus.com")

        return " ".join(query_parts)

    def search(self, make: str, model: str, year: int, location: str = "",
               num_results: int = 50) -> List[Dict]:
        """Search Google for car listings"""

        query = self.build_search_query(make, model, year, location)
        print(f"\nSearching Google: {query}")

        results = []
        start = 0

        while len(results) < num_results:
            params = {
                'q': query,
                'start': start,
                'num': 10  # Results per page
            }

            url = f"{self.base_url}?{urllib.parse.urlencode(params)}"

            soup = self.fetch_page(url)
            if not soup:
                break

            # Find search result links
            links = soup.find_all('a', href=True)

            page_results = 0
            for link in links:
                href = link['href']

                # Extract actual URL from Google redirect
                if '/url?q=' in href:
                    match = re.search(r'/url\?q=([^&]+)', href)
                    if match:
                        actual_url = urllib.parse.unquote(match.group(1))

                        # Filter for car listing sites
                        if self.is_car_listing(actual_url):
                            # Get title text
                            title = link.get_text(strip=True)

                            result = {
                                'url': actual_url,
                                'title': title,
                                'make': make,
                                'model': model,
                                'year': year,
                                'search_location': location,
                                'found_via': 'google_search'
                            }

                            if result not in results:
                                results.append(result)
                                page_results += 1
                                print(f"  Found: {actual_url[:80]}...")

            if page_results == 0:
                break  # No more results

            start += 10
            self.random_delay()

        print(f"Found {len(results)} unique listings")
        return results

    def is_car_listing(self, url: str) -> bool:
        """Check if URL is from a car listing site"""
        car_sites = [
            'craigslist.org',
            'autotrader.com',
            'cars.com',
            'cargurus.com',
            'carmax.com',
            'carvana.com',
            'vroom.com',
            'truecar.com',
            'edmunds.com',
            'kbb.com'
        ]

        return any(site in url.lower() for site in car_sites)

    def scrape_multiple_vehicles(self, vehicles: List[Dict],
                                 locations: List[str] = None) -> List[Dict]:
        """Scrape multiple vehicles and locations"""

        if locations is None:
            locations = ['']  # Empty for nationwide

        all_results = []

        for vehicle in vehicles:
            make = vehicle['make']
            model = vehicle['model']
            year = vehicle['year']

            for location in locations:
                print(f"\n{'='*60}")
                print(f"Searching: {year} {make} {model}" + (f" in {location}" if location else " nationwide"))
                print('='*60)

                results = self.search(make, model, year, location, num_results=30)
                all_results.extend(results)

                self.random_delay()

        # Save all results
        self.save_results(all_results, 'google_search_results')

        return all_results


def main():
    """Demo: Search for target vehicles"""

    scraper = GoogleScraper()

    # Target vehicles
    vehicles = [
        {'make': 'Toyota', 'model': 'Tacoma', 'year': 2024},
        {'make': 'Toyota', 'model': 'Tacoma', 'year': 2023},
        {'make': 'Toyota', 'model': 'Tacoma', 'year': 2022},
        {'make': 'Lexus', 'model': 'GX', 'year': 2024},
        {'make': 'Lexus', 'model': 'GX', 'year': 2023},
        {'make': 'Ford', 'model': 'F-150', 'year': 2024},
        {'make': 'Toyota', 'model': 'Tundra', 'year': 2024},
        {'make': 'Toyota', 'model': 'Sequoia', 'year': 2024},
        {'make': 'Tesla', 'model': 'Model Y', 'year': 2024},
    ]

    # California locations
    locations = [
        'San Francisco Bay Area',
        'Los Angeles',
        'San Diego',
        'Sacramento',
        ''  # Nationwide
    ]

    print("Starting Google search for car listings...")
    print(f"Searching {len(vehicles)} vehicles across {len(locations)} locations")
    print("This will take approximately 30-45 minutes...")

    results = scraper.scrape_multiple_vehicles(vehicles, locations)

    print(f"\n{'='*60}")
    print(f"COMPLETED: Found {len(results)} total listings")
    print('='*60)

    # Show summary
    by_site = {}
    for result in results:
        url = result['url']
        for site in ['craigslist', 'autotrader', 'cars.com', 'cargurus']:
            if site in url.lower():
                by_site[site] = by_site.get(site, 0) + 1
                break

    print("\nListings by site:")
    for site, count in sorted(by_site.items(), key=lambda x: x[1], reverse=True):
        print(f"  {site}: {count}")


if __name__ == "__main__":
    main()
