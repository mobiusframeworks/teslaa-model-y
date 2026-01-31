#!/usr/bin/env python3
"""
Google Search Results Parser
Parse vehicle listings from Google Shopping search results
"""

import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager


def extract_urls_from_google_rtf(rtf_path):
    """Extract all HYPERLINK URLs from Google RTF file"""
    with open(rtf_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Find all HYPERLINK fields
    # Format: {\field{\*\fldinst{HYPERLINK "URL"}}{\fldrslt
    url_pattern = r'\{\\field\{\\\*\\fldinst\{HYPERLINK "([^"]+)"\}\}'
    urls = re.findall(url_pattern, content)

    return urls


def parse_google_listings(text_path):
    """Parse Google Shopping listings from plain text file"""

    with open(text_path, 'r', encoding='utf-8') as f:
        content = f.read()

    listings = []

    # Split by "Visit site" to separate listings
    blocks = content.split('Visit site')

    for block in blocks:
        block = block.strip()
        if not block or len(block) < 20:
            continue

        lines = [line.strip() for line in block.split('\n') if line.strip()]

        if len(lines) < 4:
            continue

        # First line: vehicle info
        vehicle_line = lines[0]

        # Extract year, make, model
        year_match = re.search(r'(\d{4})', vehicle_line)
        if not year_match:
            continue

        year = int(year_match.group(1))

        # Extract make and model
        # Format: "2017 Lexus GX 460" or "2017 Lexus GX GX 460 SPORT UTILITY 4D"
        make = 'Lexus'

        # Extract model - everything after "Lexus"
        model_part = vehicle_line.split('Lexus', 1)[1].strip()
        # Clean up model name
        model = model_part.split('SPORT UTILITY')[0].strip()
        model = model.replace('GX GX', 'GX').strip()  # Remove duplicate GX

        # Second line: price
        price_line = lines[1]
        price_match = re.search(r'\$([0-9,]+)', price_line)
        if not price_match:
            continue

        price = float(price_match.group(1).replace(',', ''))

        # Third line: mileage
        mileage_line = lines[2]
        mileage_match = re.search(r'(\d+)k mi', mileage_line)
        if not mileage_match:
            mileage = 0
        else:
            mileage = int(mileage_match.group(1)) * 1000

        # Fourth line: source (Carfax, Autotrader, etc.)
        source = lines[3] if len(lines) > 3 else 'Google'

        # Fifth line: city (if available)
        city = None
        state = None
        for line in lines[4:8]:
            # Check if this looks like a city name (not "Cash purchase" or other text)
            if line and not any(x in line.lower() for x in ['cash', 'purchase', 'financing', 'apr', 'available', 'down', 'mileage']):
                city = line
                state = 'CA'  # Default to CA for Google searches
                break

        listing = {
            'year': year,
            'make': make,
            'model': model,
            'price': price,
            'mileage': mileage,
            'source': f'google_{source.lower().replace(" ", "_")}',
            'city': city,
            'state': state
        }

        listings.append(listing)

    return listings


def main():
    """Test parsing"""

    rtf_path = "/Users/macmini/Desktop/lexus x scrape 2017 google.rtfd/TXT.rtf"
    txt_path = "/tmp/lexus_gx_2017_google.txt"

    print("="*80)
    print("GOOGLE LISTINGS PARSER - 2017 Lexus GX")
    print("="*80)

    # Extract URLs
    print("\n1. Extracting URLs from RTF...")
    urls = extract_urls_from_google_rtf(rtf_path)
    print(f"   Found {len(urls)} URLs")

    # Parse listings
    print("\n2. Parsing listings from text...")
    listings = parse_google_listings(txt_path)
    print(f"   Found {len(listings)} listings")

    # Match URLs to listings (they should be in same order)
    print("\n3. Matching URLs to listings...")
    for i, listing in enumerate(listings):
        if i < len(urls):
            listing['source_url'] = urls[i]
        else:
            listing['source_url'] = None

    urls_matched = sum(1 for l in listings if l.get('source_url'))
    print(f"   Matched {urls_matched}/{len(listings)} URLs")

    # Display sample
    print("\n4. Sample listings:")
    print("-" * 80)
    for i, listing in enumerate(listings[:5], 1):
        url_status = "✓ URL" if listing.get('source_url') else "✗ No URL"
        print(f"{i}. {listing['year']} {listing['make']} {listing['model']} - ${listing['price']:,.0f} @ {listing['mileage']:,}mi")
        print(f"   {listing['city']}, {listing['state']} - {listing['source']} - {url_status}")

    print(f"\n{'='*80}")
    print(f"READY TO IMPORT: {len(listings)} listings")
    print(f"{'='*80}")

    return listings


if __name__ == "__main__":
    main()
