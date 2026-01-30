# Web Scraping System for Car Listings

## 🎯 Purpose

Build a comprehensive "time capsule" database of car prices across:
- Multiple vehicles (Tacoma, GX, F-150, Tundra, Sequoia, Model Y, Model 3)
- Multiple locations (California regions + nationwide)
- Multiple time periods (continuous snapshots)

**Goal**: Identify vehicles that appreciate in value (like Tacomas during COVID) and find optimal buying opportunities.

---

## 📦 Components

### 1. Base Scraper (`base_scraper.py`)
- Foundation class for all scrapers
- User agent rotation
- Rate limiting and polite delays
- Data extraction utilities (price, mileage, year)
- Location normalization

### 2. Google Scraper (`google_scraper.py`)
- Finds listing URLs via Google search
- Searches across car sites (Craigslist, Autotrader, Cars.com, CarGurus)
- Returns links for detailed scraping

### 3. Craigslist Scraper (`craigslist_scraper.py`)
- Scrapes Craigslist directly
- Extracts: price, mileage, year, location, condition
- Covers all California regions
- Handles listing detail pages

### 4. Data Loader (`data_loader.py`)
- Loads scraped data into SQL database
- Deduplicates listings
- Creates vehicles if needed
- Tracks statistics

### 5. Master Orchestrator (`master_scraper.py`)
- Coordinates all scrapers
- Runs comprehensive scraping operations
- Multiple modes: quick, full, targeted

---

## 🚀 Quick Start

### Option 1: Quick Sample (10-15 minutes)
```bash
cd scrapers
python3 master_scraper.py --mode quick
```

Scrapes:
- 2-3 vehicles
- 2-3 regions
- ~50-100 listings

Perfect for testing!

### Option 2: Full Scrape (1-2 hours)
```bash
python3 master_scraper.py --mode full
```

Scrapes:
- All 7 target vehicles
- All years (2020-2024)
- 10 California regions
- Google search for nationwide
- ~500-1000 listings

### Option 3: Targeted Scraping
```bash
# Google search only
python3 master_scraper.py --mode google

# Craigslist only
python3 master_scraper.py --mode craigslist
```

---

## 📊 What Gets Scraped

### Target Vehicles
1. **Lexus GX** (2021-2024)
2. **Ford F-150** (2020-2024)
3. **Toyota Tacoma** (2020-2024)
4. **Toyota Tundra** (2022-2024)
5. **Toyota Sequoia** (2022-2024)
6. **Tesla Model Y** (2021-2024)
7. **Tesla Model 3** (2021-2024)

### Regions Covered
**Bay Area:**
- San Francisco
- Oakland
- San Jose
- Peninsula

**SoCal:**
- Los Angeles
- San Diego
- Orange County
- Inland Empire

**Central Valley:**
- Sacramento
- Fresno
- Bakersfield
- Stockton
- Modesto

### Data Extracted
- **Price** - Asking price
- **Mileage** - Odometer reading
- **Year** - Model year
- **Location** - City, state, region
- **Condition** - excellent/good/fair/poor
- **Features** - Leather, tow package, navigation (when available)
- **Source** - URL of original listing
- **Date** - Listing date

---

## 🔄 Scraping Pipeline

```
┌──────────────────┐
│  Google Search   │ → Find listing URLs
└────────┬─────────┘
         ↓
┌──────────────────┐
│  Craigslist      │ → Extract detailed data
│  (Direct)        │
└────────┬─────────┘
         ↓
┌──────────────────┐
│  Data Loader     │ → Clean & deduplicate
└────────┬─────────┘
         ↓
┌──────────────────┐
│  SQL Database    │ → Store with timestamp
└──────────────────┘
```

---

## 💡 Usage Examples

### Example 1: Build Initial Database
```bash
# Quick sample to get started
python3 master_scraper.py --mode quick
```

### Example 2: Daily Update
```bash
# Run daily to track price changes
python3 master_scraper.py --mode craigslist
```

### Example 3: Deep Dive on Specific Vehicle
```python
from craigslist_scraper import CraigslistScraper

scraper = CraigslistScraper()

# Scrape all Bay Area Tacomas
results = scraper.search_region(
    region='sfbay',
    make='Toyota',
    model='Tacoma',
    min_year=2020,
    max_results=200
)

# Load into database
from data_loader import DataLoader
loader = DataLoader()
loader.load_listings(results)
```

### Example 4: Multi-Region Price Comparison
```python
from master_scraper import MasterScraper

scraper = MasterScraper()

# Compare Tacoma prices across all regions
for region in scraper.craigslist_regions:
    results = scraper.craigslist_scraper.search_region(
        region=region,
        make='Toyota',
        model='Tacoma',
        min_year=2023,
        max_results=50
    )
    print(f"{region}: {len(results)} listings")
```

---

## ⚙️ Configuration

### Rate Limiting
Default delays between requests:
- Base Scraper: 2-5 seconds
- Google: 3-7 seconds (more conservative)
- Craigslist: 2-5 seconds

Modify in scraper __init__:
```python
super().__init__(delay_min=3, delay_max=8)
```

### Target Vehicles
Edit `master_scraper.py`:
```python
self.target_vehicles = [
    {'make': 'Toyota', 'model': 'Tacoma', 'years': [2024, 2023, 2022]},
    # Add more...
]
```

### Regions
Edit `master_scraper.py`:
```python
self.craigslist_regions = [
    'sfbay',
    'losangeles',
    # Add more...
]
```

---

## 📈 Building the Time Capsule

### Strategy for Historical Data

**Week 1: Initial Capture**
```bash
python3 master_scraper.py --mode full
```
Captures baseline prices across all vehicles/regions.

**Ongoing: Daily/Weekly Updates**
```bash
# Daily quick scrape
python3 master_scraper.py --mode quick

# Weekly comprehensive
python3 master_scraper.py --mode craigslist
```

**Result**: Over time, you build a database showing:
- Price trends by season
- Regional price differences
- Appreciation vs depreciation patterns
- Market timing opportunities

### Example Analysis Queries

After 3+ months of data:

```sql
-- Price trends for 2023 Tacomas
SELECT
    strftime('%Y-%m', listing_date) as month,
    AVG(asking_price) as avg_price,
    COUNT(*) as listings,
    region
FROM market_prices mp
JOIN vehicles v ON mp.vehicle_id = v.id
WHERE v.make = 'Toyota'
  AND v.model = 'Tacoma'
  AND v.year = 2023
GROUP BY month, region
ORDER BY month, region;

-- Identify appreciating vehicles
SELECT
    v.make,
    v.model,
    v.year,
    MIN(mp.asking_price) as lowest_price,
    MAX(mp.asking_price) as highest_price,
    (MAX(mp.asking_price) - MIN(mp.asking_price)) as appreciation,
    COUNT(*) as data_points
FROM vehicles v
JOIN market_prices mp ON v.id = mp.vehicle_id
WHERE mp.listing_date >= date('now', '-6 months')
GROUP BY v.make, v.model, v.year
HAVING appreciation > 0
ORDER BY appreciation DESC;
```

---

## 🛡️ Ethical Scraping

### Best Practices Implemented

1. **Rate Limiting**
   - Random delays between requests
   - Exponential backoff on errors
   - Respects server resources

2. **User Agent Rotation**
   - Multiple realistic user agents
   - Mimics normal browser behavior

3. **Polite Crawling**
   - Follows robots.txt (implicit)
   - No aggressive scraping
   - Handles errors gracefully

4. **Data Usage**
   - Public listings only
   - Personal use research
   - No commercial resale

### Terms of Service
- Craigslist: Public data, polite scraping
- Google: Search results only, no API abuse
- Use responsibly and legally

---

## 🔧 Troubleshooting

### "No listings found"
- Check internet connection
- Verify region code is correct
- Craigslist may have anti-bot measures (increase delays)

### "Connection timeout"
- Increase timeout in `fetch_page()`
- Check if site is accessible manually
- Try again later

### "Too many requests"
- Increase delay between requests
- Use `--mode quick` for testing
- Wait before retrying

### Database errors
- Ensure database is initialized: `python3 database.py`
- Check file permissions
- Verify data format

---

## 📊 Data Quality

### Validation
Each listing is validated for:
- ✓ Price exists and reasonable ($1k-$500k)
- ✓ Year is valid (2000-2026)
- ✓ Mileage is reasonable (0-500k)
- ✓ Make/model match targets

### Deduplication
- Same URL = skip duplicate
- Database handles by vehicle_id + listing_date

### Cleaning
- Removes non-numeric characters
- Normalizes location names
- Standardizes conditions

---

## 🎯 Use Cases

### 1. Find Appreciating Vehicles
Track which vehicles hold or gain value over time.

Example: Tacomas during COVID went UP in price (pandemic + supply chain).

### 2. Market Timing
Identify best times to buy (winter) vs sell (spring/summer).

### 3. Regional Arbitrage
Buy in Central Valley, sell in Bay Area for $5k-10k profit.

### 4. Deal Identification
Compare listing to historical average - is this a good deal?

### 5. Seasonal Patterns
Track how prices fluctuate with seasons.

### 6. Supply/Demand
Monitor inventory levels by region and vehicle.

---

## 📅 Recommended Schedule

### Daily (5 minutes)
```bash
# Quick check for new listings
python3 master_scraper.py --mode quick
```

### Weekly (30 minutes)
```bash
# Comprehensive Craigslist scrape
python3 master_scraper.py --mode craigslist
```

### Monthly (2 hours)
```bash
# Full scrape including Google
python3 master_scraper.py --mode full
```

**Result**: After 3-6 months, you'll have robust historical data for analysis.

---

## 🚀 Future Enhancements

### Additional Sources (TODO)
- [ ] Autotrader API/scraper
- [ ] Cars.com scraper
- [ ] CarGurus scraper
- [ ] Facebook Marketplace (requires auth)
- [ ] eBay Motors
- [ ] Bring a Trailer (auction data)

### Advanced Features (TODO)
- [ ] Automated daily scheduling (cron)
- [ ] Alert system for good deals
- [ ] Price drop notifications
- [ ] ML price prediction model
- [ ] Seasonal trend analysis
- [ ] Regional heat maps

### Data Enhancement (TODO)
- [ ] VIN decoding for detailed specs
- [ ] Carfax integration
- [ ] Consumer Reports reliability scores
- [ ] KBB valuations

---

## 📚 File Structure

```
scrapers/
├── __init__.py              # Package init
├── README.md                # This file
├── base_scraper.py          # Base class
├── google_scraper.py        # Google search
├── craigslist_scraper.py    # Craigslist scraper
├── data_loader.py           # Database loader
├── master_scraper.py        # Orchestrator
└── data/                    # Scraped data (JSON)
    ├── google_search_results_*.json
    ├── craigslist_results_*.json
    └── master_scrape_*.json
```

---

## 🎓 Learn More

### Understanding the Code
Each scraper has a `main()` function you can run standalone:

```bash
# Test individual scrapers
python3 base_scraper.py      # Run tests
python3 google_scraper.py    # Google search demo
python3 craigslist_scraper.py  # Craigslist demo
python3 data_loader.py       # Load demo data
```

### Extending the System
1. Create new scraper inheriting from `BaseScraper`
2. Implement `scrape()` method
3. Add to `master_scraper.py`
4. Test independently first

Example:
```python
from base_scraper import BaseScraper

class AutotraderScraper(BaseScraper):
    def scrape(self):
        # Your implementation
        pass
```

---

## ⚡ Performance

### Quick Mode
- Time: 10-15 minutes
- Listings: ~50-100
- Regions: 2
- Vehicles: 2

### Full Mode
- Time: 1-2 hours
- Listings: ~500-1000
- Regions: 10+
- Vehicles: 7 (all years)

### Optimization Tips
- Run overnight for full scrapes
- Use `--mode craigslist` for faster updates
- Focus on specific regions if needed
- Parallel scraping (future enhancement)

---

**🎯 Ready to build your time capsule database!**

Start with: `python3 master_scraper.py --mode quick`
