#!/usr/bin/env python3
"""
Parse Facebook Marketplace RTF files for Tesla listings
"""

import re
import sys
from pathlib import Path

def parse_facebook_rtf(rtf_path):
    """Extract Tesla listings from Facebook Marketplace RTF file"""

    with open(rtf_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Extract URLs
    url_pattern = r'\{\\field\{\\\*\\fldinst\{HYPERLINK "([^"]+)"\}\}'
    urls = re.findall(url_pattern, content)

    # Extract prices (format: $XX,XXX or $X,XXX)
    price_pattern = r'\$([0-9,]+)'
    prices = re.findall(price_pattern, content)

    # Extract vehicle descriptions (year + make + model)
    # Match patterns like "2022 Tesla Model 3 Long Range AWD"
    vehicle_pattern = r'(\d{4})\s+(Tesla)\s+(Model\s+[3SXY])[^\\n]*'
    vehicles = re.findall(vehicle_pattern, content, re.IGNORECASE)

    # Extract cities
    city_pattern = r'([A-Z][a-z\s]+),\s*CA'
    cities = re.findall(city_pattern, content)

    # Extract mileage if present
    mileage_pattern = r'(\d+)K?\s*miles'
    mileages = re.findall(mileage_pattern, content)

    # Combine into listings
    listings = []

    min_length = min(len(urls), len(prices), len(vehicles))

    for i in range(min_length):
        url = urls[i] if i < len(urls) else None
        price_str = prices[i].replace(',', '')
        price = int(price_str) if price_str.isdigit() else None

        year, make, model = vehicles[i]
        year = int(year)

        city = cities[i] if i < len(cities) else "Unknown"

        # Try to find mileage
        mileage = None
        if i < len(mileages):
            try:
                mileage = int(mileages[i].replace('K', '').replace(',', '')) * 1000
            except:
                mileage = None

        listing = {
            'year': year,
            'make': make,
            'model': model.strip(),
            'price': price,
            'mileage': mileage,
            'city': city.strip(),
            'state': 'CA',
            'source': 'facebook_marketplace',
            'source_url': url
        }

        listings.append(listing)

    return listings


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python parse_facebook_rtf.py <path_to_rtf>")
        sys.exit(1)

    rtf_path = sys.argv[1]
    listings = parse_facebook_rtf(rtf_path)

    print(f"Found {len(listings)} listings:")
    for listing in listings:
        print(f"  {listing['year']} {listing['make']} {listing['model']} - ${listing['price']:,} - {listing.get('mileage', 'Unknown')} mi - {listing['city']}, {listing['state']}")
