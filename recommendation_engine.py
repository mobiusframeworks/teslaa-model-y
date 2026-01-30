"""
Vehicle Recommendation Engine
Matches users with ideal vehicles or vehicle combinations
Considers: budget, needs, driver fit, total cost of ownership
"""

from database import DatabaseManager, VehicleRepository, MarketPriceRepository, DriverFitRepository, ProblemRepository
from scoring_engine import VehicleScorer, UserPreferences
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import json


@dataclass
class UseCase:
    """Specific use case requirements"""
    name: str
    description: str
    min_cargo: float = 0
    min_towing: int = 0
    min_seats: int = 5
    prefer_fuel_efficiency: bool = False
    prefer_reliability: bool = True
    prefer_comfort: bool = True
    off_road_capable: bool = False


class RecommendationEngine:
    """Generate vehicle recommendations based on user needs"""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self.vehicle_repo = VehicleRepository(db)
        self.price_repo = MarketPriceRepository(db)
        self.fit_repo = DriverFitRepository(db)
        self.problem_repo = ProblemRepository(db)
        self.scorer = VehicleScorer(db)

    def find_best_matches(self, preferences: UserPreferences, limit: int = 10) -> List[Dict]:
        """
        Find best vehicle matches for user preferences
        Returns scored and ranked listings
        """
        # Get all available listings
        listings = self.price_repo.get_listings()

        # Filter by hard requirements
        filtered_listings = []
        for listing in listings:
            vehicle = self.vehicle_repo.get_vehicle(listing['vehicle_id'])
            fit_data = self.fit_repo.get_fit_data(listing['vehicle_id'])

            # Budget check
            if listing['asking_price'] > preferences.budget_max:
                continue

            # Mileage check
            if listing['mileage'] > preferences.max_mileage:
                continue

            # 4WD requirement
            if preferences.require_4wd and vehicle['drivetrain'] not in ['4WD', 'AWD']:
                continue

            # Tall driver requirement
            if preferences.require_tall_driver_suitable and fit_data:
                if not fit_data['tall_driver_suitable']:
                    continue

            # Height compatibility
            if fit_data:
                if preferences.driver_height < fit_data['recommended_height_min'] or \
                   preferences.driver_height > fit_data['recommended_height_max']:
                    continue

            # Cargo requirement
            if vehicle['cargo_capacity_cuft'] < preferences.min_cargo_cuft:
                continue

            # Towing requirement
            if vehicle['towing_capacity_lbs'] < preferences.min_towing_lbs:
                continue

            filtered_listings.append(listing)

        # Score remaining listings
        scored_listings = []
        for listing in filtered_listings:
            try:
                score_result = self.scorer.score_listing(listing, preferences)
                scored_listings.append({
                    'listing': listing,
                    'score': score_result
                })
            except Exception as e:
                print(f"Error scoring listing {listing.get('id')}: {e}")

        # Sort by total score
        scored_listings.sort(key=lambda x: x['score']['total_score'], reverse=True)

        return scored_listings[:limit]

    def analyze_use_case(self, use_case: UseCase, budget: float, driver_height: int) -> Dict:
        """
        Analyze which vehicles are best for a specific use case
        Returns recommendations and analysis
        """
        # Build preferences from use case
        prefs = UserPreferences(
            budget_max=budget,
            driver_height=driver_height,
            min_cargo_cuft=use_case.min_cargo,
            min_towing_lbs=use_case.min_towing,
            require_4wd=use_case.off_road_capable,
            max_mileage=100000
        )

        # Adjust weights based on use case priorities
        if use_case.prefer_fuel_efficiency:
            prefs.weight_maintenance = 0.20  # Includes fuel efficiency
            prefs.weight_price = 0.20
            prefs.weight_reliability = 0.20
            prefs.weight_comfort = 0.15
            prefs.weight_features = 0.15
            prefs.weight_resale = 0.10

        if use_case.prefer_reliability:
            prefs.weight_reliability = 0.30
            prefs.weight_resale = 0.15
            prefs.weight_price = 0.20
            prefs.weight_comfort = 0.15
            prefs.weight_features = 0.15
            prefs.weight_maintenance = 0.05

        if use_case.prefer_comfort:
            prefs.weight_comfort = 0.30
            prefs.weight_reliability = 0.20
            prefs.weight_features = 0.20
            prefs.weight_price = 0.15
            prefs.weight_resale = 0.10
            prefs.weight_maintenance = 0.05

        # Find best matches
        matches = self.find_best_matches(prefs, limit=5)

        return {
            'use_case': use_case.name,
            'description': use_case.description,
            'preferences': prefs,
            'top_matches': matches,
            'total_found': len(matches)
        }

    def compare_ownership_scenarios(self, vehicle_ids: List[int], budget: float, years: int = 3) -> Dict:
        """
        Compare total cost of ownership for different vehicles
        Helps decide between options
        """
        comparisons = []

        for vehicle_id in vehicle_ids:
            vehicle = self.vehicle_repo.get_vehicle(vehicle_id)

            # Get market data
            listings = self.price_repo.get_listings(vehicle_id=vehicle_id)
            if not listings:
                continue

            avg_price = sum(l['asking_price'] for l in listings) / len(listings)
            avg_mileage = sum(l['mileage'] for l in listings) / len(listings)

            # Calculate ownership costs
            annual_miles = 15000
            total_miles = annual_miles * years

            # Fuel/electricity costs
            if vehicle['fuel_type'] == 'electric':
                fuel_cost = total_miles * 0.04  # $0.04/mile
            else:
                mpg = vehicle.get('mpg_combined', 20)
                gallons = total_miles / mpg
                fuel_cost = gallons * 3.50

            # Maintenance (rough estimate)
            if vehicle['fuel_type'] == 'electric':
                maintenance_cost = total_miles * 0.05
            else:
                maintenance_cost = total_miles * 0.10

            # Insurance (rough estimate based on value)
            annual_insurance = avg_price * 0.03  # 3% of value
            total_insurance = annual_insurance * years

            # Depreciation estimate
            depreciation_rate = 0.15  # 15% per year average
            if vehicle['make'] in ['Toyota', 'Lexus']:
                depreciation_rate = 0.12  # Better retention
            elif vehicle['make'] == 'Tesla':
                depreciation_rate = 0.20  # Higher depreciation currently

            end_value = avg_price * ((1 - depreciation_rate) ** years)
            total_depreciation = avg_price - end_value

            # Total cost of ownership
            tco = avg_price + fuel_cost + maintenance_cost + total_insurance - end_value

            comparisons.append({
                'vehicle': f"{vehicle['year']} {vehicle['make']} {vehicle['model']} {vehicle['trim']}",
                'avg_purchase_price': round(avg_price, 0),
                'avg_mileage': round(avg_mileage, 0),
                'fuel_cost': round(fuel_cost, 0),
                'maintenance_cost': round(maintenance_cost, 0),
                'insurance_cost': round(total_insurance, 0),
                'depreciation': round(total_depreciation, 0),
                'estimated_end_value': round(end_value, 0),
                'total_cost_of_ownership': round(tco, 0),
                'monthly_equivalent': round(tco / (years * 12), 0)
            })

        # Sort by TCO
        comparisons.sort(key=lambda x: x['total_cost_of_ownership'])

        return {
            'comparison_period_years': years,
            'vehicles_compared': len(comparisons),
            'comparisons': comparisons
        }

    def find_dual_vehicle_strategy(self, budget: float, driver_height: int) -> Dict:
        """
        Find optimal dual-vehicle strategy
        E.g., efficient daily driver + capable weekend warrior
        """
        # Strategy: One efficient vehicle + one capable truck/SUV
        # Split budget 40/60 or 50/50

        daily_driver_budget = budget * 0.40
        adventure_budget = budget * 0.60

        # Find efficient daily driver
        daily_prefs = UserPreferences(
            budget_max=daily_driver_budget,
            driver_height=driver_height,
            min_cargo_cuft=20,
            min_towing_lbs=0,
            require_4wd=False,
            max_mileage=80000,
            weight_price=0.25,
            weight_maintenance=0.25,  # Emphasize efficiency
            weight_reliability=0.20,
            weight_comfort=0.20,
            weight_features=0.05,
            weight_resale=0.05
        )

        daily_matches = self.find_best_matches(daily_prefs, limit=3)

        # Find adventure vehicle
        adventure_prefs = UserPreferences(
            budget_max=adventure_budget,
            driver_height=driver_height,
            min_cargo_cuft=60,
            min_towing_lbs=5000,
            require_4wd=True,
            require_tall_driver_suitable=True,
            max_mileage=80000,
            weight_features=0.30,  # Emphasize capability
            weight_reliability=0.25,
            weight_comfort=0.20,
            weight_price=0.15,
            weight_resale=0.05,
            weight_maintenance=0.05
        )

        adventure_matches = self.find_best_matches(adventure_prefs, limit=3)

        # Calculate combined strategies
        strategies = []
        for daily in daily_matches[:2]:
            for adventure in adventure_matches[:2]:
                total_cost = daily['listing']['asking_price'] + adventure['listing']['asking_price']
                if total_cost <= budget:
                    strategies.append({
                        'daily_driver': {
                            'vehicle': f"{daily['score']['vehicle_details']['year']} {daily['score']['vehicle_details']['make']} {daily['score']['vehicle_details']['model']}",
                            'price': daily['listing']['asking_price'],
                            'score': daily['score']['total_score']
                        },
                        'adventure_vehicle': {
                            'vehicle': f"{adventure['score']['vehicle_details']['year']} {adventure['score']['vehicle_details']['make']} {adventure['score']['vehicle_details']['model']}",
                            'price': adventure['listing']['asking_price'],
                            'score': adventure['score']['total_score']
                        },
                        'total_cost': total_cost,
                        'combined_score': (daily['score']['total_score'] + adventure['score']['total_score']) / 2
                    })

        strategies.sort(key=lambda x: x['combined_score'], reverse=True)

        return {
            'budget': budget,
            'daily_driver_candidates': len(daily_matches),
            'adventure_vehicle_candidates': len(adventure_matches),
            'viable_strategies': strategies
        }


def main():
    """Demo the recommendation engine"""
    db = DatabaseManager()
    recommender = RecommendationEngine(db)

    print("=" * 80)
    print("VEHICLE RECOMMENDATION ENGINE")
    print("=" * 80)

    # Example 1: Find best matches for a tall driver with outdoor needs
    print("\n\nEXAMPLE 1: Tall Driver (6'3\") with Outdoor Lifestyle")
    print("-" * 80)

    prefs = UserPreferences(
        budget_max=70000,
        driver_height=75,
        min_comfort_score=7,
        min_cargo_cuft=60,
        min_towing_lbs=5000,
        require_4wd=True,
        require_tall_driver_suitable=True,
        max_mileage=50000
    )

    matches = recommender.find_best_matches(prefs, limit=5)

    print(f"Found {len(matches)} matches\n")
    for i, match in enumerate(matches, 1):
        veh = match['score']['vehicle_details']
        listing = match['listing']
        score = match['score']

        print(f"{i}. {veh['year']} {veh['make']} {veh['model']} {veh['trim']}")
        print(f"   Price: ${listing['asking_price']:,.0f} | Mileage: {listing['mileage']:,}")
        print(f"   Score: {score['total_score']}/100 | {score['deal_quality']}")
        print(f"   {score['recommendation']}")
        print()

    # Example 2: Use case analysis
    print("\n\nEXAMPLE 2: Mountain Biking & Camping Use Case")
    print("-" * 80)

    outdoor_use = UseCase(
        name="Mountain Biking & Camping",
        description="Weekend warrior needing cargo space, towing, and off-road capability",
        min_cargo=70,
        min_towing=5000,
        prefer_reliability=True,
        prefer_comfort=True,
        off_road_capable=True
    )

    result = recommender.analyze_use_case(outdoor_use, budget=70000, driver_height=75)

    print(f"Use Case: {result['use_case']}")
    print(f"{result['description']}\n")
    print(f"Found {result['total_found']} suitable vehicles:\n")

    for i, match in enumerate(result['top_matches'], 1):
        veh = match['score']['vehicle_details']
        print(f"{i}. {veh['year']} {veh['make']} {veh['model']} - Score: {match['score']['total_score']}/100")

    # Example 3: TCO Comparison
    print("\n\nEXAMPLE 3: Total Cost of Ownership Comparison (3 years)")
    print("-" * 80)

    # Get some vehicle IDs to compare
    vehicles = recommender.vehicle_repo.find_vehicles()
    vehicle_ids = [v['id'] for v in vehicles[:4]]

    tco_result = recommender.compare_ownership_scenarios(vehicle_ids, budget=70000, years=3)

    print(f"Comparing {tco_result['vehicles_compared']} vehicles over {tco_result['comparison_period_years']} years:\n")

    for comp in tco_result['comparisons']:
        print(f"{comp['vehicle']}")
        print(f"  Purchase: ${comp['avg_purchase_price']:,.0f}")
        print(f"  Fuel: ${comp['fuel_cost']:,.0f}")
        print(f"  Maintenance: ${comp['maintenance_cost']:,.0f}")
        print(f"  Insurance: ${comp['insurance_cost']:,.0f}")
        print(f"  Depreciation: ${comp['depreciation']:,.0f}")
        print(f"  End Value: ${comp['estimated_end_value']:,.0f}")
        print(f"  ➜ TOTAL TCO: ${comp['total_cost_of_ownership']:,.0f} (${comp['monthly_equivalent']:,.0f}/month)")
        print()

    print("\n" + "=" * 80)
    print("RECOMMENDATION ENGINE DEMO COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
