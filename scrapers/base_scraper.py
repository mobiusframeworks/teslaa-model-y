"""
Base Web Scraper
Foundation for all car listing scrapers
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from typing import Dict, List, Optional
from datetime import datetime
import json
from urllib.parse import urljoin, urlparse
import re


class BaseScraper:
    """Base class for all scrapers"""

    def __init__(self, delay_min=2, delay_max=5):
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.session = requests.Session()

        # Rotate user agents to avoid detection
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]

    def get_headers(self) -> Dict:
        """Get randomized headers"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def random_delay(self):
        """Random delay between requests"""
        time.sleep(random.uniform(self.delay_min, self.delay_max))

    def fetch_page(self, url: str, max_retries: int = 3) -> Optional[BeautifulSoup]:
        """Fetch and parse a page with retries"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, headers=self.get_headers(), timeout=30)
                response.raise_for_status()

                return BeautifulSoup(response.content, 'html.parser')

            except requests.RequestException as e:
                print(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5 * (attempt + 1))  # Exponential backoff
                else:
                    print(f"Failed to fetch {url} after {max_retries} attempts")
                    return None

    def extract_price(self, text: str) -> Optional[float]:
        """Extract price from text"""
        if not text:
            return None

        # Remove common price prefixes
        text = text.replace('$', '').replace(',', '').strip()

        # Find numbers
        match = re.search(r'(\d+(?:\.\d+)?)', text)
        if match:
            try:
                price = float(match.group(1))
                # Sanity check: reasonable car prices
                if 1000 <= price <= 500000:
                    return price
            except ValueError:
                pass

        return None

    def extract_mileage(self, text: str) -> Optional[int]:
        """Extract mileage from text"""
        if not text:
            return None

        # Remove common suffixes
        text = text.lower().replace(',', '').replace('mi', '').replace('miles', '').strip()

        match = re.search(r'(\d+)', text)
        if match:
            try:
                mileage = int(match.group(1))
                # Sanity check
                if 0 <= mileage <= 500000:
                    return mileage
            except ValueError:
                pass

        return None

    def extract_year(self, text: str) -> Optional[int]:
        """Extract year from text"""
        if not text:
            return None

        match = re.search(r'(20\d{2})', text)
        if match:
            try:
                year = int(match.group(1))
                current_year = datetime.now().year
                if 2000 <= year <= current_year + 1:
                    return year
            except ValueError:
                pass

        return None

    def normalize_location(self, location: str) -> Dict[str, str]:
        """Normalize location into city, state, region"""
        if not location:
            return {'city': '', 'state': '', 'region': ''}

        location = location.strip()

        # Try to parse city, state
        parts = [p.strip() for p in location.split(',')]

        city = parts[0] if len(parts) > 0 else ''
        state = parts[1] if len(parts) > 1 else ''

        # Determine region (simplified California focus)
        region = self.get_california_region(city, state)

        return {
            'city': city,
            'state': state,
            'region': region
        }

    def get_california_region(self, city: str, state: str) -> str:
        """Get California region from city"""
        if state.upper() not in ['CA', 'CALIFORNIA']:
            return 'Out of State'

        city = city.lower()

        # Bay Area cities
        bay_area = [
            'san francisco', 'oakland', 'berkeley', 'san jose', 'fremont',
            'palo alto', 'mountain view', 'sunnyvale', 'santa clara',
            'redwood city', 'san mateo', 'hayward', 'alameda', 'daly city',
            'san rafael', 'vallejo', 'fairfield', 'vacaville'
        ]

        # SoCal cities
        socal = [
            'los angeles', 'san diego', 'long beach', 'anaheim', 'santa ana',
            'irvine', 'riverside', 'santa monica', 'pasadena', 'torrance',
            'orange', 'fullerton', 'huntington beach', 'newport beach'
        ]

        # Central Valley
        central_valley = [
            'fresno', 'bakersfield', 'stockton', 'modesto', 'sacramento',
            'visalia', 'salinas', 'merced', 'turlock', 'madera'
        ]

        for bay_city in bay_area:
            if bay_city in city:
                return 'Bay Area'

        for socal_city in socal:
            if socal_city in city:
                return 'SoCal'

        for cv_city in central_valley:
            if cv_city in city:
                return 'Central Valley'

        return 'Other CA'

    def save_results(self, results: List[Dict], filename: str):
        """Save scraping results to JSON"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = f"scrapers/data/{filename}_{timestamp}.json"

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"Saved {len(results)} results to {filepath}")

    def scrape(self) -> List[Dict]:
        """Override in subclass"""
        raise NotImplementedError("Subclass must implement scrape()")


def test_base_scraper():
    """Test base scraper utilities"""
    scraper = BaseScraper()

    # Test price extraction
    assert scraper.extract_price("$45,000") == 45000
    assert scraper.extract_price("Price: $32,500") == 32500

    # Test mileage extraction
    assert scraper.extract_mileage("45,000 mi") == 45000
    assert scraper.extract_mileage("12000 miles") == 12000

    # Test year extraction
    assert scraper.extract_year("2024 Toyota Tacoma") == 2024

    # Test location
    loc = scraper.normalize_location("San Jose, CA")
    assert loc['city'] == 'San Jose'
    assert loc['state'] == 'CA'
    assert loc['region'] == 'Bay Area'

    print("✓ Base scraper tests passed!")


if __name__ == "__main__":
    test_base_scraper()
