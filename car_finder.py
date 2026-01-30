#!/usr/bin/env python3
"""
Car Finder - Comprehensive Vehicle Valuation and Deal Finding System
Main CLI interface for the car valuation database
"""

from database import DatabaseManager, Vehicle, MarketPrice, VehicleProblem, DriverFit
from database import VehicleRepository, MarketPriceRepository, ProblemRepository, DriverFitRepository
from scoring_engine import VehicleScorer, UserPreferences
from recommendation_engine import RecommendationEngine, UseCase
from market_analysis import MarketAnalyzer
import sys


class CarFinder:
    """Main application interface"""

    def __init__(self):
        self.db = DatabaseManager()
        self.vehicle_repo = VehicleRepository(self.db)
        self.price_repo = MarketPriceRepository(self.db)
        self.problem_repo = ProblemRepository(self.db)
        self.fit_repo = DriverFitRepository(self.db)
        self.scorer = VehicleScorer(self.db)
        self.recommender = RecommendationEngine(self.db)
        self.market_analyzer = MarketAnalyzer(self.db)

    def show_menu(self):
        """Display main menu"""
        print("\n" + "=" * 80)
        print("CAR VALUATION & DEAL FINDER SYSTEM".center(80))
        print("=" * 80)
        print("\n[1] Find Best Vehicles for My Needs")
        print("[2] Score a Specific Listing")
        print("[3] View All Available Listings")
        print("[4] Analyze Market by Region")
        print("[5] Find Underpriced Deals")
        print("[6] Compare Total Cost of Ownership")
        print("[7] View Vehicle Problems & Reliability")
        print("[8] Check Driver Fit for Tall Drivers")
        print("[9] Add New Listing")
        print("[10] View Market Heat / Conditions")
        print("[0] Exit")
        print("-" * 80)

    def find_best_vehicles(self):
        """Interactive vehicle recommendation"""
        print("\n" + "=" * 80)
        print("FIND YOUR IDEAL VEHICLE")
        print("=" * 80)

        # Get user inputs
        try:
            budget = float(input("\nMax budget ($): "))
            height_ft = int(input("Your height (feet): "))
            height_in = int(input("Additional inches: "))
            driver_height = height_ft * 12 + height_in

            print("\nWhat do you need the vehicle for?")
            print("[1] Daily commute (efficiency priority)")
            print("[2] Outdoor adventures (cargo, towing, 4WD)")
            print("[3] Family hauler (space, comfort)")
            print("[4] Balanced (good at everything)")

            use_type = input("\nChoice (1-4): ")

            # Set preferences based on use type
            if use_type == "1":
                min_cargo = 20
                min_towing = 0
                require_4wd = False
                prefs = UserPreferences(
                    budget_max=budget,
                    driver_height=driver_height,
                    min_cargo_cuft=min_cargo,
                    min_towing_lbs=min_towing,
                    require_4wd=require_4wd,
                    max_mileage=100000,
                    weight_maintenance=0.30,
                    weight_price=0.25,
                    weight_reliability=0.20,
                    weight_comfort=0.15,
                    weight_features=0.05,
                    weight_resale=0.05
                )
            elif use_type == "2":
                min_cargo = 60
                min_towing = 5000
                require_4wd = True
                prefs = UserPreferences(
                    budget_max=budget,
                    driver_height=driver_height,
                    min_cargo_cuft=min_cargo,
                    min_towing_lbs=min_towing,
                    require_4wd=require_4wd,
                    require_tall_driver_suitable=True if driver_height >= 75 else False,
                    max_mileage=80000,
                    weight_features=0.30,
                    weight_reliability=0.25,
                    weight_comfort=0.20,
                    weight_price=0.15,
                    weight_resale=0.05,
                    weight_maintenance=0.05
                )
            elif use_type == "3":
                min_cargo = 80
                min_towing = 3000
                require_4wd = False
                prefs = UserPreferences(
                    budget_max=budget,
                    driver_height=driver_height,
                    min_cargo_cuft=min_cargo,
                    min_towing_lbs=min_towing,
                    require_4wd=require_4wd,
                    max_mileage=80000,
                    weight_comfort=0.30,
                    weight_features=0.25,
                    weight_reliability=0.20,
                    weight_price=0.15,
                    weight_resale=0.05,
                    weight_maintenance=0.05
                )
            else:
                min_cargo = 40
                min_towing = 3000
                require_4wd = False
                prefs = UserPreferences(
                    budget_max=budget,
                    driver_height=driver_height,
                    min_cargo_cuft=min_cargo,
                    min_towing_lbs=min_towing,
                    require_4wd=require_4wd,
                    max_mileage=80000
                )

            # Find matches
            matches = self.recommender.find_best_matches(prefs, limit=10)

            if not matches:
                print("\nNo vehicles found matching your criteria.")
                print("Try adjusting your requirements or budget.")
                return

            print(f"\n\nFound {len(matches)} vehicles matching your needs:\n")
            print("=" * 80)

            for i, match in enumerate(matches, 1):
                veh = match['score']['vehicle_details']
                listing = match['listing']
                score = match['score']

                print(f"\n#{i}. {veh['year']} {veh['make']} {veh['model']} {veh['trim']}")
                print(f"    Price: ${listing['asking_price']:,.0f} | Fair Value: ${score['fair_market_value']:,.0f}")
                print(f"    Mileage: {listing['mileage']:,} | Condition: {listing.get('condition', 'Good')}")
                print(f"    Location: {listing.get('city', 'N/A')}, {listing.get('region', 'N/A')}")
                print(f"\n    SCORE: {score['total_score']}/100 - {score['deal_quality']}")
                print(f"    {score['recommendation']}")
                print(f"\n    Breakdown:")
                for category, value in score['scores_breakdown'].items():
                    bar_length = int(value / 5)
                    bar = "█" * bar_length + "░" * (20 - bar_length)
                    print(f"      {category.capitalize():<15}: {bar} {value:.1f}/100")

            print("\n" + "=" * 80)

        except ValueError:
            print("Invalid input. Please try again.")
        except KeyboardInterrupt:
            print("\nCancelled.")

    def view_listings(self):
        """View all available listings"""
        print("\n" + "=" * 80)
        print("ALL AVAILABLE LISTINGS")
        print("=" * 80)

        listings = self.price_repo.get_listings()

        if not listings:
            print("\nNo listings found in database.")
            return

        print(f"\nTotal: {len(listings)} listings\n")

        for listing in listings:
            print(f"\n{listing['year']} {listing['make']} {listing['model']} {listing.get('trim', '')}")
            print(f"  Price: ${listing['asking_price']:,.0f}")
            print(f"  Mileage: {listing['mileage']:,}")
            print(f"  Condition: {listing.get('condition', 'Unknown')}")
            print(f"  Location: {listing.get('city', 'N/A')}, {listing.get('region', 'N/A')}")
            if listing.get('sold'):
                print(f"  SOLD for ${listing.get('sale_price', 0):,.0f}")
            print(f"  ID: {listing['id']}")

    def analyze_market(self):
        """Analyze market by region"""
        print("\n" + "=" * 80)
        print("REGIONAL MARKET ANALYSIS")
        print("=" * 80)

        make = input("\nMake (e.g., Toyota): ")
        model = input("Model (e.g., Tacoma): ")
        year = input("Year (optional, press Enter to skip): ")

        year = int(year) if year else None

        result = self.market_analyzer.analyze_regional_pricing(make, model, year)

        if 'error' in result:
            print(f"\n{result['error']}")
            return

        print(f"\nVehicle: {result['vehicle']}\n")
        print("=" * 80)

        for region, stats in result['regional_stats'].items():
            print(f"\n{region}:")
            print(f"  Listings: {stats['listing_count']}")
            print(f"  Average Price: ${stats['avg_asking_price']:,.0f}")
            print(f"  Median Price: ${stats['median_asking_price']:,.0f}")
            print(f"  Range: ${stats['min_price']:,.0f} - ${stats['max_price']:,.0f}")
            print(f"  Avg Mileage: {stats['avg_mileage']:,}")
            if stats['avg_sale_price']:
                print(f"  Avg Sale Price: ${stats['avg_sale_price']:,.0f}")
                print(f"  Sold: {stats['sold_count']}/{stats['listing_count']}")

        if result['arbitrage_opportunity']:
            arb = result['arbitrage_opportunity']
            print("\n" + "=" * 80)
            print("ARBITRAGE OPPORTUNITY DETECTED!")
            print("=" * 80)
            print(f"\n  Buy from: {arb['buy_from']}")
            print(f"  Avg Price: ${arb['buy_price']:,.0f}")
            print(f"\n  Sell to: {arb['sell_to']}")
            print(f"  Avg Price: ${arb['sell_price']:,.0f}")
            print(f"\n  Potential Profit: ${arb['potential_profit']:,.0f}")
            print(f"  Profit Margin: {arb['profit_percentage']}%")
            print("\n  Note: Subtract transport costs, registration, sales tax")

    def find_deals(self):
        """Find underpriced listings"""
        print("\n" + "=" * 80)
        print("FIND UNDERPRICED DEALS")
        print("=" * 80)

        threshold = input("\nMin discount % (default 10%): ")
        threshold = float(threshold) if threshold else 10.0

        deals = self.market_analyzer.find_underpriced_listings(threshold_pct=threshold)

        if not deals:
            print(f"\nNo listings found at least {threshold}% below market average.")
            return

        print(f"\nFound {len(deals)} underpriced listings:\n")
        print("=" * 80)

        for i, deal in enumerate(deals, 1):
            print(f"\n#{i}. {deal['vehicle']}")
            print(f"    Asking Price: ${deal['asking_price']:,.0f}")
            print(f"    Market Avg: ${deal['market_avg']:,.0f}")
            print(f"    SAVINGS: ${deal['savings']:,.0f} ({deal['savings_pct']}% below market)")
            print(f"    Mileage: {deal['mileage']:,}")
            print(f"    Condition: {deal['condition']}")
            print(f"    Location: {deal['location']}")
            print(f"    Listing ID: {deal['listing_id']}")

    def view_problems(self):
        """View vehicle problems and reliability"""
        print("\n" + "=" * 80)
        print("VEHICLE PROBLEMS & RELIABILITY")
        print("=" * 80)

        make = input("\nMake: ")
        model = input("Model: ")
        year = input("Year (optional): ")

        year = int(year) if year else None

        problems = self.problem_repo.get_problems(make, model, year)

        if not problems:
            print(f"\nNo known problems found for {make} {model}" + (f" {year}" if year else ""))
            print("This could mean:")
            print("  - Excellent reliability")
            print("  - No data yet in database")
            return

        print(f"\nKnown problems for {make} {model}:\n")
        print("=" * 80)

        for prob in problems:
            years = f"{prob['year_start']}-{prob['year_end']}" if prob['year_start'] != prob['year_end'] else str(prob['year_start'])
            print(f"\nYears: {years} | Category: {prob['problem_category']}")
            print(f"  {prob['problem_description']}")
            print(f"  Severity: {prob['severity'].upper()} | Frequency: {prob['frequency']}")
            if prob['avg_repair_cost'] > 0:
                print(f"  Avg Repair Cost: ${prob['avg_repair_cost']:,.0f}")
            if prob['has_tsb']:
                print(f"  TSB: {prob['tsb_number']}")
            if prob['has_recall']:
                print(f"  RECALL: {prob['recall_number']}")
            if prob['notes']:
                print(f"  Notes: {prob['notes']}")

    def check_driver_fit(self):
        """Check vehicles suitable for tall drivers"""
        print("\n" + "=" * 80)
        print("DRIVER FIT ANALYSIS FOR TALL DRIVERS")
        print("=" * 80)

        height_ft = int(input("\nYour height (feet): "))
        height_in = int(input("Additional inches: "))
        driver_height = height_ft * 12 + height_in

        min_comfort = int(input("Minimum comfort score (1-10, default 7): ") or "7")

        suitable = self.fit_repo.find_suitable_vehicles(driver_height, min_comfort)

        if not suitable:
            print(f"\nNo vehicles found suitable for {driver_height}\" height with {min_comfort}+ comfort score.")
            return

        print(f"\nFound {len(suitable)} suitable vehicles:\n")
        print("=" * 80)

        for veh in suitable:
            print(f"\n{veh['year']} {veh['make']} {veh['model']} {veh.get('trim', '')}")
            print(f"  Seat Comfort: {veh['seat_comfort_score']}/10")
            print(f"  Adjustability: {veh['seat_adjustability_score']}/10")
            print(f"  Legroom: F:{veh['legroom_front_in']}\" / R:{veh['legroom_rear_in']}\"")
            print(f"  Headroom: F:{veh['headroom_front_in']}\" / R:{veh['headroom_rear_in']}\"")
            if veh['tall_driver_notes']:
                print(f"  Notes: {veh['tall_driver_notes']}")

    def add_listing(self):
        """Add a new market listing"""
        print("\n" + "=" * 80)
        print("ADD NEW LISTING")
        print("=" * 80)

        try:
            # Find or select vehicle
            make = input("\nMake: ")
            model = input("Model: ")
            year = int(input("Year: "))

            vehicles = self.vehicle_repo.find_vehicles(make=make, model=model, year_min=year, year_max=year)

            if not vehicles:
                print(f"\nNo {year} {make} {model} found in database.")
                print("Please add the vehicle to the database first.")
                return

            vehicle = vehicles[0]
            print(f"\nFound: {vehicle['year']} {vehicle['make']} {vehicle['model']} {vehicle.get('trim', '')}")

            # Get listing details
            asking_price = float(input("\nAsking price ($): "))
            mileage = int(input("Mileage: "))
            condition = input("Condition (excellent/good/fair/poor): ") or "good"
            city = input("City: ")
            region = input("Region (e.g., Bay Area): ")

            has_leather = input("Has leather? (y/n): ").lower() == 'y'
            has_tow = input("Has tow package? (y/n): ").lower() == 'y'
            has_nav = input("Has navigation? (y/n): ").lower() == 'y'

            # Create listing
            listing = MarketPrice(
                vehicle_id=vehicle['id'],
                listing_date="2024-01-29",  # Today
                mileage=mileage,
                asking_price=asking_price,
                condition=condition,
                city=city,
                region=region,
                has_leather=has_leather,
                has_tow_package=has_tow,
                has_nav=has_nav,
                source="manual"
            )

            listing_id = self.price_repo.add_listing(listing)

            print(f"\n✓ Listing added successfully! ID: {listing_id}")

        except ValueError:
            print("\nInvalid input. Please try again.")
        except KeyboardInterrupt:
            print("\nCancelled.")

    def market_heat(self):
        """Show market conditions"""
        print("\n" + "=" * 80)
        print("MARKET CONDITIONS & HEAT")
        print("=" * 80)

        heat = self.market_analyzer.calculate_market_heat()

        if 'error' in heat:
            print(f"\n{heat['error']}")
            return

        print(f"\nTotal Listings: {heat['total_listings']}")
        print(f"Sold: {heat['sold_listings']} ({heat['sell_through_rate']}%)")
        print(f"\nMarket Condition: {heat['market_condition']}")
        print(f"\nBuyer Advice: {heat['buyer_advice']}")

        print(f"\n\nSupply Breakdown:")
        print("-" * 80)
        for vehicle, count in sorted(heat['supply_by_vehicle'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {vehicle}: {count} listings")

    def run(self):
        """Main application loop"""
        print("\nWelcome to Car Valuation & Deal Finder System!")

        while True:
            self.show_menu()

            choice = input("\nSelect option (0-10): ")

            if choice == "1":
                self.find_best_vehicles()
            elif choice == "2":
                print("\nFeature coming soon: Score specific listing")
            elif choice == "3":
                self.view_listings()
            elif choice == "4":
                self.analyze_market()
            elif choice == "5":
                self.find_deals()
            elif choice == "6":
                print("\nFeature coming soon: TCO comparison")
            elif choice == "7":
                self.view_problems()
            elif choice == "8":
                self.check_driver_fit()
            elif choice == "9":
                self.add_listing()
            elif choice == "10":
                self.market_heat()
            elif choice == "0":
                print("\nThank you for using Car Finder!")
                break
            else:
                print("\nInvalid choice. Please try again.")

            input("\nPress Enter to continue...")


def main():
    """Entry point"""
    app = CarFinder()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)


if __name__ == "__main__":
    main()
