"""
Market Analysis and Arbitrage Tools
Compare prices across different California markets
Identify best markets to buy from and sell into
"""

from database import DatabaseManager, VehicleRepository, MarketPriceRepository
from typing import Dict, List, Optional
from collections import defaultdict
import statistics


class MarketAnalyzer:
    """Analyze market trends and identify arbitrage opportunities"""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self.vehicle_repo = VehicleRepository(db)
        self.price_repo = MarketPriceRepository(db)

    def analyze_regional_pricing(self, make: str, model: str, year: int = None) -> Dict:
        """
        Analyze pricing differences across regions
        Returns price statistics by region
        """
        # Get all listings for this vehicle
        vehicles = self.vehicle_repo.find_vehicles(make=make, model=model)

        if year:
            vehicles = [v for v in vehicles if v['year'] == year]

        if not vehicles:
            return {'error': 'No vehicles found'}

        vehicle_ids = [v['id'] for v in vehicles]

        # Group listings by region
        regional_data = defaultdict(list)

        for vehicle_id in vehicle_ids:
            listings = self.price_repo.get_listings(vehicle_id=vehicle_id)

            for listing in listings:
                if listing.get('region'):
                    regional_data[listing['region']].append({
                        'price': listing['asking_price'],
                        'mileage': listing['mileage'],
                        'condition': listing.get('condition', 'good'),
                        'sold': listing.get('sold', False),
                        'sale_price': listing.get('sale_price')
                    })

        # Calculate statistics for each region
        regional_stats = {}

        for region, listings in regional_data.items():
            prices = [l['price'] for l in listings]
            mileages = [l['mileage'] for l in listings]

            sold_listings = [l for l in listings if l['sold'] and l['sale_price']]
            sale_prices = [l['sale_price'] for l in sold_listings] if sold_listings else []

            regional_stats[region] = {
                'listing_count': len(listings),
                'avg_asking_price': round(statistics.mean(prices), 0) if prices else 0,
                'median_asking_price': round(statistics.median(prices), 0) if prices else 0,
                'min_price': round(min(prices), 0) if prices else 0,
                'max_price': round(max(prices), 0) if prices else 0,
                'price_std_dev': round(statistics.stdev(prices), 0) if len(prices) > 1 else 0,
                'avg_mileage': round(statistics.mean(mileages), 0) if mileages else 0,
                'sold_count': len(sold_listings),
                'avg_sale_price': round(statistics.mean(sale_prices), 0) if sale_prices else None
            }

        # Identify arbitrage opportunities
        if len(regional_stats) > 1:
            # Find cheapest and most expensive markets
            cheapest_region = min(regional_stats.items(), key=lambda x: x[1]['avg_asking_price'])
            most_expensive_region = max(regional_stats.items(), key=lambda x: x[1]['avg_asking_price'])

            price_difference = most_expensive_region[1]['avg_asking_price'] - cheapest_region[1]['avg_asking_price']
            arbitrage_percentage = (price_difference / cheapest_region[1]['avg_asking_price']) * 100

            arbitrage_opportunity = {
                'buy_from': cheapest_region[0],
                'buy_price': cheapest_region[1]['avg_asking_price'],
                'sell_to': most_expensive_region[0],
                'sell_price': most_expensive_region[1]['avg_asking_price'],
                'potential_profit': price_difference,
                'profit_percentage': round(arbitrage_percentage, 1)
            }
        else:
            arbitrage_opportunity = None

        return {
            'vehicle': f"{make} {model}" + (f" {year}" if year else ""),
            'regional_stats': regional_stats,
            'arbitrage_opportunity': arbitrage_opportunity
        }

    def find_best_buy_markets(self, limit: int = 5) -> List[Dict]:
        """
        Identify markets with best prices (good for buying)
        Returns list of regions sorted by average price
        """
        # Get all listings
        listings = self.price_repo.get_listings()

        # Group by region
        regional_prices = defaultdict(list)
        for listing in listings:
            if listing.get('region'):
                regional_prices[listing['region']].append(listing['asking_price'])

        # Calculate averages
        market_scores = []
        for region, prices in regional_prices.items():
            if len(prices) >= 2:  # Need at least 2 listings
                market_scores.append({
                    'region': region,
                    'avg_price': round(statistics.mean(prices), 0),
                    'median_price': round(statistics.median(prices), 0),
                    'listing_count': len(prices),
                    'price_range': round(max(prices) - min(prices), 0)
                })

        # Sort by average price (lowest first = best to buy)
        market_scores.sort(key=lambda x: x['avg_price'])

        return market_scores[:limit]

    def find_best_sell_markets(self, limit: int = 5) -> List[Dict]:
        """
        Identify markets with highest prices (good for selling)
        Returns list of regions sorted by average price (highest first)
        """
        markets = self.find_best_buy_markets(limit=100)
        markets.reverse()  # Highest prices first
        return markets[:limit]

    def analyze_price_trends(self, make: str, model: str) -> Dict:
        """
        Analyze price trends over time
        (Limited by current data - would be better with more historical data)
        """
        vehicles = self.vehicle_repo.find_vehicles(make=make, model=model)

        if not vehicles:
            return {'error': 'No vehicles found'}

        vehicle_ids = [v['id'] for v in vehicles]

        # Get all listings
        all_listings = []
        for vehicle_id in vehicle_ids:
            listings = self.price_repo.get_listings(vehicle_id=vehicle_id)
            all_listings.extend(listings)

        # Group by year
        by_year = defaultdict(list)
        for listing in all_listings:
            year = listing.get('year', 'Unknown')
            by_year[year].append({
                'price': listing['asking_price'],
                'mileage': listing['mileage'],
                'sold': listing.get('sold', False)
            })

        # Calculate statistics by year
        year_stats = {}
        for year, listings in by_year.items():
            prices = [l['price'] for l in listings]
            sold_count = sum(1 for l in listings if l['sold'])

            year_stats[year] = {
                'listing_count': len(listings),
                'avg_price': round(statistics.mean(prices), 0) if prices else 0,
                'min_price': round(min(prices), 0) if prices else 0,
                'max_price': round(max(prices), 0) if prices else 0,
                'sold_count': sold_count,
                'sell_through_rate': round(sold_count / len(listings) * 100, 1) if listings else 0
            }

        return {
            'vehicle': f"{make} {model}",
            'year_stats': year_stats,
            'total_listings': len(all_listings)
        }

    def calculate_market_heat(self) -> Dict:
        """
        Calculate market "heat" - seller's market vs buyer's market
        High inventory + low sold rate = buyer's market
        Low inventory + high sold rate = seller's market
        """
        # Get all listings
        listings = self.price_repo.get_listings()

        total_listings = len(listings)
        sold_listings = sum(1 for l in listings if l.get('sold', False))

        if total_listings == 0:
            return {'error': 'No market data available'}

        sell_through_rate = (sold_listings / total_listings) * 100

        # Group by make/model for supply analysis
        vehicle_counts = defaultdict(int)
        for listing in listings:
            vehicle_counts[f"{listing['make']} {listing['model']}"] += 1

        # Determine market condition
        if sell_through_rate > 60:
            if total_listings < 10:
                market_condition = "Hot Seller's Market"
                advice = "Prices likely rising. Act fast on good deals."
            else:
                market_condition = "Seller's Market"
                advice = "Demand is high. Negotiate carefully."
        elif sell_through_rate > 40:
            market_condition = "Balanced Market"
            advice = "Fair negotiating power on both sides."
        else:
            if total_listings > 20:
                market_condition = "Buyer's Market"
                advice = "High supply, low demand. Good time to negotiate."
            else:
                market_condition = "Slow Buyer's Market"
                advice = "Excellent negotiating position. Lowball offers may work."

        return {
            'total_listings': total_listings,
            'sold_listings': sold_listings,
            'sell_through_rate': round(sell_through_rate, 1),
            'market_condition': market_condition,
            'buyer_advice': advice,
            'supply_by_vehicle': dict(vehicle_counts)
        }

    def find_underpriced_listings(self, threshold_pct: float = 10) -> List[Dict]:
        """
        Find listings that are priced below market average
        Good candidates for quick purchases
        """
        underpriced = []

        # Get all unique vehicles
        vehicles = self.vehicle_repo.find_vehicles()

        for vehicle in vehicles:
            # Get market stats for this vehicle
            stats = self.price_repo.get_market_statistics(
                vehicle['make'],
                vehicle['model'],
                vehicle['year']
            )

            if not stats or not stats.get('avg_price'):
                continue

            avg_price = stats['avg_price']

            # Get individual listings
            listings = self.price_repo.get_listings(vehicle_id=vehicle['id'])

            for listing in listings:
                if listing.get('sold'):
                    continue  # Skip sold listings

                price_diff_pct = ((listing['asking_price'] - avg_price) / avg_price) * 100

                if price_diff_pct <= -threshold_pct:
                    underpriced.append({
                        'vehicle': f"{vehicle['year']} {vehicle['make']} {vehicle['model']} {vehicle['trim']}",
                        'asking_price': listing['asking_price'],
                        'market_avg': round(avg_price, 0),
                        'savings': round(avg_price - listing['asking_price'], 0),
                        'savings_pct': round(-price_diff_pct, 1),
                        'mileage': listing['mileage'],
                        'condition': listing.get('condition', 'Unknown'),
                        'location': f"{listing.get('city', 'Unknown')}, {listing.get('region', 'Unknown')}",
                        'listing_id': listing['id']
                    })

        # Sort by savings percentage
        underpriced.sort(key=lambda x: x['savings_pct'], reverse=True)

        return underpriced


def main():
    """Demo market analysis tools"""
    db = DatabaseManager()
    analyzer = MarketAnalyzer(db)

    print("=" * 80)
    print("MARKET ANALYSIS & ARBITRAGE TOOLS")
    print("=" * 80)

    # Example 1: Regional pricing analysis
    print("\n\nREGIONAL PRICING ANALYSIS - Toyota Tacoma")
    print("-" * 80)

    regional = analyzer.analyze_regional_pricing("Toyota", "Tacoma", 2024)

    if 'error' not in regional:
        print(f"Vehicle: {regional['vehicle']}\n")

        for region, stats in regional['regional_stats'].items():
            print(f"{region}:")
            print(f"  Listings: {stats['listing_count']}")
            print(f"  Avg Price: ${stats['avg_asking_price']:,.0f}")
            print(f"  Range: ${stats['min_price']:,.0f} - ${stats['max_price']:,.0f}")
            print(f"  Avg Mileage: {stats['avg_mileage']:,}")
            if stats['avg_sale_price']:
                print(f"  Avg Sale Price: ${stats['avg_sale_price']:,.0f}")
            print()

        if regional['arbitrage_opportunity']:
            arb = regional['arbitrage_opportunity']
            print("ARBITRAGE OPPORTUNITY:")
            print(f"  Buy from: {arb['buy_from']} at ~${arb['buy_price']:,.0f}")
            print(f"  Sell to: {arb['sell_to']} at ~${arb['sell_price']:,.0f}")
            print(f"  Potential Profit: ${arb['potential_profit']:,.0f} ({arb['profit_percentage']}%)")
    else:
        print(regional['error'])

    # Example 2: Best markets to buy
    print("\n\nBEST MARKETS TO BUY FROM")
    print("-" * 80)

    buy_markets = analyzer.find_best_buy_markets(limit=5)

    for i, market in enumerate(buy_markets, 1):
        print(f"{i}. {market['region']}")
        print(f"   Avg Price: ${market['avg_price']:,.0f}")
        print(f"   Listings: {market['listing_count']}")
        print(f"   Price Range: ${market['price_range']:,.0f}")
        print()

    # Example 3: Best markets to sell
    print("\nBEST MARKETS TO SELL INTO")
    print("-" * 80)

    sell_markets = analyzer.find_best_sell_markets(limit=5)

    for i, market in enumerate(sell_markets, 1):
        print(f"{i}. {market['region']}")
        print(f"   Avg Price: ${market['avg_price']:,.0f}")
        print(f"   Listings: {market['listing_count']}")
        print()

    # Example 4: Market heat
    print("\nMARKET CONDITION")
    print("-" * 80)

    heat = analyzer.calculate_market_heat()

    if 'error' not in heat:
        print(f"Total Listings: {heat['total_listings']}")
        print(f"Sold: {heat['sold_listings']} ({heat['sell_through_rate']}%)")
        print(f"\nMarket Condition: {heat['market_condition']}")
        print(f"Advice: {heat['buyer_advice']}")
        print(f"\nSupply by Vehicle:")
        for vehicle, count in sorted(heat['supply_by_vehicle'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {vehicle}: {count} listings")
    else:
        print(heat['error'])

    # Example 5: Underpriced listings
    print("\n\nUNDERPRICED LISTINGS (10%+ below market)")
    print("-" * 80)

    deals = analyzer.find_underpriced_listings(threshold_pct=10)

    if deals:
        for i, deal in enumerate(deals[:5], 1):
            print(f"{i}. {deal['vehicle']}")
            print(f"   Asking: ${deal['asking_price']:,.0f} | Market Avg: ${deal['market_avg']:,.0f}")
            print(f"   Savings: ${deal['savings']:,.0f} ({deal['savings_pct']}% below market)")
            print(f"   Mileage: {deal['mileage']:,} | Condition: {deal['condition']}")
            print(f"   Location: {deal['location']}")
            print()
    else:
        print("No significantly underpriced listings found in current data.")

    print("\n" + "=" * 80)
    print("MARKET ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
