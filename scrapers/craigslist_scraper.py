"""
Craigslist Scraper
Extract detailed listings from Craigslist
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_scraper import BaseScraper
from typing import List, Dict, Optional
import re


class CraigslistScraper(BaseScraper):
    """Scrape Craigslist car listings"""

    def search_region(self, region: str, make: str, model: str,
                     min_year: int = 2020, max_results: int = 100) -> List[Dict]:
        """
        Search Craigslist in a specific region
        region: sfbay, losangeles, sandiego, sacramento, etc.
        """

        base_url = f"https://{region}.craigslist.org/search/cta"

        # Build search parameters
        search_query = f"{make} {model}"

        results = []
        offset = 0

        while len(results) < max_results:
            # Craigslist search URL
            params = f"?query={search_query}&min_auto_year={min_year}&sort=date"
            if offset > 0:
                params += f"&s={offset}"

            url = base_url + params

            print(f"Scraping: {url}")

            soup = self.fetch_page(url)
            if not soup:
                break

            # Find listing results
            listings = soup.find_all('li', class_='cl-search-result')

            if not listings:
                print("No more listings found")
                break

            for listing in listings:
                try:
                    result = self.parse_listing_preview(listing, region)
                    if result:
                        results.append(result)
                        print(f"  Found: {result['year']} {result['make']} {result['model']} - ${result['price']:,}")

                except Exception as e:
                    print(f"Error parsing listing: {e}")
                    continue

            offset += len(listings)
            self.random_delay()

        return results

    def parse_listing_preview(self, listing, region: str) -> Optional[Dict]:
        """Parse a listing from search results"""

        # Get link
        link_elem = listing.find('a', class_='cl-app-anchor')
        if not link_elem:
            return None

        url = link_elem.get('href', '')
        if not url.startswith('http'):
            url = f"https://{region}.craigslist.org{url}"

        # Get title
        title_elem = listing.find('div', class_='title')
        title = title_elem.get_text(strip=True) if title_elem else ''

        # Get price
        price_elem = listing.find('div', class_='price')
        price_text = price_elem.get_text(strip=True) if price_elem else ''
        price = self.extract_price(price_text)

        # Get meta info (mileage, location)
        meta_elem = listing.find('div', class_='meta')
        meta_text = meta_elem.get_text(strip=True) if meta_elem else ''

        mileage = self.extract_mileage(meta_text)

        # Extract year from title
        year = self.extract_year(title)

        # Parse make/model from title
        make, model = self.parse_make_model_from_title(title)

        # Get location from meta
        location_parts = meta_text.split('·')
        location_text = location_parts[0].strip() if location_parts else ''
        location = self.normalize_location(location_text)

        return {
            'url': url,
            'title': title,
            'price': price,
            'year': year,
            'make': make,
            'model': model,
            'mileage': mileage,
            'city': location['city'],
            'state': location['state'],
            'region': location['region'] if location['region'] != 'Out of State' else self.region_from_craigslist(region),
            'source': 'craigslist',
            'listing_date': None  # Would need to fetch detail page
        }

    def parse_listing_detail(self, url: str) -> Optional[Dict]:
        """Parse detailed listing page"""

        soup = self.fetch_page(url)
        if not soup:
            return None

        result = {
            'url': url,
            'source': 'craigslist'
        }

        # Title
        title_elem = soup.find('span', id='titletextonly')
        if title_elem:
            result['title'] = title_elem.get_text(strip=True)

        # Price
        price_elem = soup.find('span', class_='price')
        if price_elem:
            result['price'] = self.extract_price(price_elem.get_text())

        # Attributes
        attrs = soup.find_all('p', class_='attrgroup')
        for attr_group in attrs:
            spans = attr_group.find_all('span')
            for span in spans:
                text = span.get_text(strip=True).lower()

                if 'odometer' in text:
                    result['mileage'] = self.extract_mileage(text)
                elif 'condition' in text:
                    # Extract condition: "condition: excellent"
                    result['condition'] = text.split(':')[-1].strip()
                elif 'vin' in text:
                    result['vin'] = text.split(':')[-1].strip()
                elif 'cylinders' in text:
                    result['cylinders'] = text.split(':')[-1].strip()
                elif 'drive' in text:
                    result['drivetrain'] = text.split(':')[-1].strip()
                elif 'fuel' in text:
                    result['fuel_type'] = text.split(':')[-1].strip()
                elif 'transmission' in text:
                    result['transmission'] = text.split(':')[-1].strip()

        # Location
        map_elem = soup.find('div', id='map')
        if map_elem:
            location_text = map_elem.get('data-location', '')
            if location_text:
                location = self.normalize_location(location_text)
                result.update(location)

        # Description
        body_elem = soup.find('section', id='postingbody')
        if body_elem:
            result['description'] = body_elem.get_text(strip=True)

        # Parse make/model from title
        if 'title' in result:
            result['year'] = self.extract_year(result['title'])
            make, model = self.parse_make_model_from_title(result['title'])
            result['make'] = make
            result['model'] = model

        return result

    def parse_make_model_from_title(self, title: str) -> tuple:
        """Extract make and model from title"""
        title = title.lower()

        # Known makes
        makes = {
            'toyota': ['tacoma', 'tundra', 'sequoia', '4runner', 'highlander'],
            'lexus': ['gx', 'lx', 'rx', 'nx'],
            'ford': ['f-150', 'f150', 'f-250', 'f250'],
            'tesla': ['model y', 'model 3', 'model s', 'model x'],
            'chevrolet': ['silverado', 'tahoe', 'suburban'],
            'gmc': ['sierra', 'yukon']
        }

        for make, models in makes.items():
            if make in title:
                for model in models:
                    if model in title:
                        return make.title(), model.title()

        return '', ''

    def region_from_craigslist(self, region_code: str) -> str:
        """Map Craigslist region code to our regions"""
        mapping = {
            'sfbay': 'Bay Area',
            'sac': 'Central Valley',
            'sacramento': 'Central Valley',
            'losangeles': 'SoCal',
            'sandiego': 'SoCal',
            'orangecounty': 'SoCal',
            'inlandempire': 'SoCal',
            'fresno': 'Central Valley',
            'bakersfield': 'Central Valley',
            'stockton': 'Central Valley',
            'modesto': 'Central Valley'
        }

        return mapping.get(region_code, 'Other CA')


def main():
    """Demo: Scrape Craigslist"""

    scraper = CraigslistScraper()

    # California regions
    regions = [
        'sfbay',        # Bay Area
        'sacramento',   # Sacramento
        'losangeles',   # LA
        'sandiego',     # San Diego
        'fresno',       # Central Valley
    ]

    # Target vehicles
    targets = [
        {'make': 'Toyota', 'model': 'Tacoma'},
        {'make': 'Lexus', 'model': 'GX'},
        {'make': 'Toyota', 'model': 'Tundra'},
    ]

    all_results = []

    for region in regions:
        for target in targets:
            print(f"\n{'='*60}")
            print(f"Searching {region} for {target['make']} {target['model']}")
            print('='*60)

            results = scraper.search_region(
                region=region,
                make=target['make'],
                model=target['model'],
                min_year=2020,
                max_results=50
            )

            all_results.extend(results)

            print(f"Found {len(results)} listings in {region}")
            scraper.random_delay()

    # Save results
    scraper.save_results(all_results, 'craigslist_results')

    print(f"\n{'='*60}")
    print(f"TOTAL: Found {len(all_results)} listings across all regions")
    print('='*60)


if __name__ == "__main__":
    main()
