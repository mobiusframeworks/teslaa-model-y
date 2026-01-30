"""
Comprehensive Scoring and Analysis Engine
Multi-factor scoring to identify best value vehicles
"""

from database import DatabaseManager, VehicleRepository, MarketPriceRepository, ProblemRepository, DriverFitRepository
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserPreferences:
    """User requirements and priorities"""
    budget_max: float
    driver_height: int  # inches
    min_comfort_score: int = 7
    min_cargo_cuft: float = 0
    min_towing_lbs: int = 0
    require_4wd: bool = False
    require_tall_driver_suitable: bool = False
    max_mileage: int = 100000
    preferred_regions: List[str] = None

    # Priority weights (should sum to 1.0)
    weight_price: float = 0.25  # Value for money
    weight_reliability: float = 0.25  # Long-term dependability
    weight_comfort: float = 0.20  # Driver fit and comfort
    weight_features: float = 0.15  # Cargo, towing, etc.
    weight_resale: float = 0.10  # Depreciation/resale value
    weight_maintenance: float = 0.05  # Cost to maintain


class VehicleScorer:
    """Calculate comprehensive scores for vehicles"""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self.vehicle_repo = VehicleRepository(db)
        self.price_repo = MarketPriceRepository(db)
        self.problem_repo = ProblemRepository(db)
        self.fit_repo = DriverFitRepository(db)

    def score_listing(self, listing: Dict, preferences: UserPreferences) -> Dict:
        """
        Calculate comprehensive score for a market listing
        Returns detailed scoring breakdown
        """
        vehicle_id = listing['vehicle_id']
        vehicle = self.vehicle_repo.get_vehicle(vehicle_id)
        fit_data = self.fit_repo.get_fit_data(vehicle_id)
        problems = self.problem_repo.get_problems(vehicle['make'], vehicle['model'], vehicle['year'])

        scores = {}

        # 1. Price Score (0-100)
        scores['price'] = self._score_price(listing, vehicle, preferences)

        # 2. Reliability Score (0-100)
        scores['reliability'] = self._score_reliability(vehicle, problems)

        # 3. Comfort/Fit Score (0-100)
        scores['comfort'] = self._score_comfort(vehicle, fit_data, preferences)

        # 4. Features Score (0-100)
        scores['features'] = self._score_features(vehicle, listing, preferences)

        # 5. Resale Value Score (0-100)
        scores['resale'] = self._score_resale(vehicle, listing)

        # 6. Maintenance Cost Score (0-100)
        scores['maintenance'] = self._score_maintenance(vehicle, listing)

        # Calculate weighted total
        total_score = (
            scores['price'] * preferences.weight_price +
            scores['reliability'] * preferences.weight_reliability +
            scores['comfort'] * preferences.weight_comfort +
            scores['features'] * preferences.weight_features +
            scores['resale'] * preferences.weight_resale +
            scores['maintenance'] * preferences.weight_maintenance
        )

        # Calculate fair market value
        fair_value = self._calculate_fair_value(vehicle, listing)
        price_diff = listing['asking_price'] - fair_value
        price_diff_pct = (price_diff / fair_value) * 100

        return {
            'total_score': round(total_score, 1),
            'scores_breakdown': {k: round(v, 1) for k, v in scores.items()},
            'fair_market_value': round(fair_value, 0),
            'asking_price': listing['asking_price'],
            'price_difference': round(price_diff, 0),
            'price_difference_pct': round(price_diff_pct, 1),
            'deal_quality': self._classify_deal(price_diff_pct, total_score),
            'recommendation': self._generate_recommendation(total_score, price_diff_pct, problems),
            'vehicle_details': {
                'make': vehicle['make'],
                'model': vehicle['model'],
                'year': vehicle['year'],
                'trim': vehicle['trim']
            }
        }

    def _score_price(self, listing: Dict, vehicle: Dict, preferences: UserPreferences) -> float:
        """Score based on price relative to budget and market"""
        asking_price = listing['asking_price']

        # Price vs budget
        if asking_price > preferences.budget_max:
            budget_score = 0
        else:
            # Better score for prices well under budget
            budget_utilization = asking_price / preferences.budget_max
            budget_score = 100 * (1 - budget_utilization * 0.7)  # Max 30% penalty for using full budget

        # Price vs market average
        market_stats = self.price_repo.get_market_statistics(
            vehicle['make'], vehicle['model'], vehicle['year']
        )

        if market_stats and market_stats.get('avg_price'):
            price_vs_market = asking_price / market_stats['avg_price']
            if price_vs_market < 0.85:  # 15%+ below market
                market_score = 100
            elif price_vs_market < 0.95:  # 5-15% below market
                market_score = 80
            elif price_vs_market < 1.05:  # Within 5% of market
                market_score = 60
            elif price_vs_market < 1.15:  # 5-15% above market
                market_score = 40
            else:  # 15%+ above market
                market_score = 20
        else:
            market_score = 50  # No data, neutral

        # Average budget and market scores
        return (budget_score + market_score) / 2

    def _score_reliability(self, vehicle: Dict, problems: List[Dict]) -> float:
        """Score based on known problems and brand reputation"""

        # Brand reliability baseline
        brand_scores = {
            'Toyota': 95,
            'Lexus': 98,
            'Ford': 70,
            'Tesla': 65,
            'Chevrolet': 68,
            'GMC': 68,
            'RAM': 65,
            'Nissan': 72,
            'Honda': 90,
            'Acura': 88
        }

        base_score = brand_scores.get(vehicle['make'], 75)

        # Deduct for known problems
        problem_penalty = 0
        for problem in problems:
            if problem['severity'] == 'critical':
                problem_penalty += 20
            elif problem['severity'] == 'major':
                problem_penalty += 10
            elif problem['severity'] == 'moderate':
                problem_penalty += 5
            elif problem['severity'] == 'minor':
                problem_penalty += 2

            # Extra penalty for common/widespread problems
            if problem['frequency'] == 'widespread':
                problem_penalty += 5
            elif problem['frequency'] == 'common':
                problem_penalty += 3

        final_score = base_score - problem_penalty
        return max(0, min(100, final_score))

    def _score_comfort(self, vehicle: Dict, fit_data: Dict, preferences: UserPreferences) -> float:
        """Score based on driver fit and comfort"""

        if not fit_data:
            return 50  # No data, neutral score

        # Height compatibility
        driver_height = preferences.driver_height
        if driver_height < fit_data['recommended_height_min'] or driver_height > fit_data['recommended_height_max']:
            height_score = 30  # Not recommended for this height
        elif preferences.require_tall_driver_suitable and not fit_data['tall_driver_suitable']:
            height_score = 20  # Required but not suitable
        else:
            height_score = 100

        # Comfort scores (already 1-10, convert to 0-100)
        seat_comfort = fit_data['seat_comfort_score'] * 10
        lumbar = fit_data['lumbar_support_score'] * 10
        adjustability = fit_data['seat_adjustability_score'] * 10

        # Average all comfort factors
        avg_comfort = (height_score + seat_comfort + lumbar + adjustability) / 4

        return avg_comfort

    def _score_features(self, vehicle: Dict, listing: Dict, preferences: UserPreferences) -> float:
        """Score based on cargo, towing, and desired features"""
        score = 50  # Base score

        # Cargo capacity
        if vehicle['cargo_capacity_cuft'] >= preferences.min_cargo_cuft:
            cargo_excess = vehicle['cargo_capacity_cuft'] - preferences.min_cargo_cuft
            score += min(25, cargo_excess / 2)  # Up to +25 for extra cargo

        # Towing capacity
        if vehicle['towing_capacity_lbs'] >= preferences.min_towing_lbs:
            if vehicle['towing_capacity_lbs'] >= 8000:
                score += 25  # Heavy duty towing
            elif vehicle['towing_capacity_lbs'] >= 5000:
                score += 15  # Good towing
            else:
                score += 10  # Light towing

        # 4WD/AWD
        if preferences.require_4wd:
            if vehicle['drivetrain'] in ['4WD', 'AWD']:
                score += 10
            else:
                score -= 30  # Major penalty if required but missing

        # Desirable features
        if listing.get('has_leather'):
            score += 5
        if listing.get('has_tow_package'):
            score += 5
        if listing.get('has_nav'):
            score += 3

        return max(0, min(100, score))

    def _score_resale(self, vehicle: Dict, listing: Dict) -> float:
        """Score based on depreciation and resale value retention"""

        # Brands with strong resale
        strong_resale_brands = {
            'Toyota': 90,
            'Lexus': 85,
            'Honda': 85,
            'Ford': 75,  # F-150 specifically holds value well
            'Tesla': 60,  # Currently depreciating rapidly
            'Chevrolet': 65,
            'GMC': 70,
        }

        brand_score = strong_resale_brands.get(vehicle['make'], 70)

        # Model-specific adjustments
        if vehicle['model'] in ['Tacoma', '4Runner', 'Land Cruiser', 'GX', 'LX']:
            brand_score += 10  # These are value retention champions

        if vehicle['model'] == 'F-150':
            brand_score += 5  # Best-selling truck, holds value

        # Mileage factor
        mileage = listing['mileage']
        if mileage < 20000:
            mileage_score = 100
        elif mileage < 50000:
            mileage_score = 85
        elif mileage < 75000:
            mileage_score = 70
        elif mileage < 100000:
            mileage_score = 55
        else:
            mileage_score = 40

        # Condition factor
        condition_scores = {
            'excellent': 100,
            'good': 85,
            'fair': 65,
            'poor': 40
        }
        condition_score = condition_scores.get(listing.get('condition', 'good'), 70)

        # Average factors
        return (brand_score * 0.5 + mileage_score * 0.3 + condition_score * 0.2)

    def _score_maintenance(self, vehicle: Dict, listing: Dict) -> float:
        """Score based on expected maintenance costs"""

        # Fuel type efficiency
        if vehicle['fuel_type'] == 'electric':
            fuel_score = 100  # Cheapest to "fuel"
            maintenance_base = 90  # EVs have lower maintenance
        elif vehicle['fuel_type'] == 'hybrid':
            mpg = vehicle.get('mpg_combined', 20)
            fuel_score = min(100, mpg * 3)  # Up to 100 for 33+ mpg
            maintenance_base = 75  # Hybrids more complex
        else:
            mpg = vehicle.get('mpg_combined', 20)
            fuel_score = min(100, mpg * 4)  # Up to 100 for 25+ mpg
            maintenance_base = 70

        # Brand maintenance cost (reliability correlates with lower maintenance)
        brand_maintenance = {
            'Toyota': 90,
            'Lexus': 75,  # More expensive than Toyota
            'Honda': 88,
            'Ford': 70,
            'Tesla': 80,  # Low maintenance but expensive repairs
            'Chevrolet': 68,
            'GMC': 68
        }

        brand_score = brand_maintenance.get(vehicle['make'], 70)

        # Age/mileage factor - older/higher mileage = more maintenance
        mileage = listing['mileage']
        if mileage < 30000:
            age_score = 100
        elif mileage < 60000:
            age_score = 85
        elif mileage < 100000:
            age_score = 70
        else:
            age_score = 55

        return (fuel_score * 0.3 + maintenance_base * 0.3 + brand_score * 0.2 + age_score * 0.2)

    def _calculate_fair_value(self, vehicle: Dict, listing: Dict) -> float:
        """Estimate fair market value"""
        msrp = vehicle.get('msrp', 50000)
        mileage = listing['mileage']
        condition = listing.get('condition', 'good')

        # Basic depreciation curve
        age = datetime.now().year - vehicle['year']

        # Year 0: 90% of MSRP
        # Year 1: 75%
        # Year 2: 65%
        # Year 3: 55%
        # Year 5: 45%

        if age == 0:
            base_value = msrp * 0.90
        elif age == 1:
            base_value = msrp * 0.75
        elif age == 2:
            base_value = msrp * 0.65
        elif age == 3:
            base_value = msrp * 0.55
        elif age == 4:
            base_value = msrp * 0.50
        else:
            base_value = msrp * max(0.30, 0.50 - (age - 4) * 0.04)

        # Mileage adjustment
        expected_mileage = age * 12000
        mileage_diff = mileage - expected_mileage

        if mileage_diff > 0:
            # Higher than expected mileage = depreciation
            mileage_penalty = min(mileage_diff * 0.10, base_value * 0.20)  # Max 20% penalty
            base_value -= mileage_penalty
        else:
            # Lower mileage = premium
            mileage_bonus = min(abs(mileage_diff) * 0.08, base_value * 0.10)  # Max 10% bonus
            base_value += mileage_bonus

        # Condition adjustment
        condition_multipliers = {
            'excellent': 1.10,
            'good': 1.00,
            'fair': 0.85,
            'poor': 0.65
        }
        base_value *= condition_multipliers.get(condition, 1.00)

        # Feature adjustments
        if listing.get('has_leather'):
            base_value += 1500
        if listing.get('has_tow_package'):
            base_value += 1000
        if listing.get('has_nav'):
            base_value += 800

        return base_value

    def _classify_deal(self, price_diff_pct: float, total_score: float) -> str:
        """Classify the deal quality"""
        if price_diff_pct <= -15 and total_score >= 75:
            return "Excellent Deal"
        elif price_diff_pct <= -10 and total_score >= 70:
            return "Very Good Deal"
        elif price_diff_pct <= -5 and total_score >= 65:
            return "Good Deal"
        elif price_diff_pct <= 5 and total_score >= 60:
            return "Fair Deal"
        elif price_diff_pct <= 10:
            return "Slightly Overpriced"
        else:
            return "Overpriced"

    def _generate_recommendation(self, total_score: float, price_diff_pct: float, problems: List[Dict]) -> str:
        """Generate buying recommendation"""
        if total_score >= 80 and price_diff_pct <= -10:
            return "STRONG BUY - Excellent vehicle at great price"
        elif total_score >= 70 and price_diff_pct <= -5:
            return "BUY - Good vehicle at fair price"
        elif total_score >= 65 and price_diff_pct <= 5:
            return "CONSIDER - Decent option, negotiate lower"
        elif total_score >= 60:
            return "HOLD - Explore other options first"
        elif len([p for p in problems if p['severity'] in ['critical', 'major']]) > 0:
            return "AVOID - Known major problems with this model"
        else:
            return "AVOID - Better options available"


def main():
    """Demo the scoring engine"""
    db = DatabaseManager()
    scorer = VehicleScorer(db)
    price_repo = MarketPriceRepository(db)

    # Example user preferences
    prefs = UserPreferences(
        budget_max=70000,
        driver_height=75,  # 6'3"
        min_comfort_score=7,
        min_cargo_cuft=60,
        min_towing_lbs=5000,
        require_4wd=True,
        require_tall_driver_suitable=True,
        max_mileage=50000,
        weight_price=0.25,
        weight_reliability=0.25,
        weight_comfort=0.20,
        weight_features=0.15,
        weight_resale=0.10,
        weight_maintenance=0.05
    )

    print("=" * 80)
    print("VEHICLE SCORING ENGINE - DEMO")
    print("=" * 80)
    print(f"\nUser Profile:")
    print(f"  Budget: ${prefs.budget_max:,.0f}")
    print(f"  Height: {prefs.driver_height}\" ({prefs.driver_height // 12}'{prefs.driver_height % 12}\")")
    print(f"  Min Cargo: {prefs.min_cargo_cuft} cu ft")
    print(f"  Min Towing: {prefs.min_towing_lbs:,} lbs")
    print(f"  Requires: 4WD, Tall Driver Suitable")

    # Get all listings
    listings = price_repo.get_listings()

    print(f"\n\nAnalyzing {len(listings)} listings...\n")
    print("=" * 80)

    scored_listings = []
    for listing in listings:
        try:
            score_result = scorer.score_listing(listing, prefs)
            scored_listings.append((listing, score_result))
        except Exception as e:
            print(f"Error scoring listing {listing.get('id')}: {e}")

    # Sort by total score
    scored_listings.sort(key=lambda x: x[1]['total_score'], reverse=True)

    # Display results
    for listing, score in scored_listings:
        veh = score['vehicle_details']
        print(f"\n{veh['year']} {veh['make']} {veh['model']} {veh['trim']}")
        print(f"  Mileage: {listing['mileage']:,} | Asking: ${listing['asking_price']:,.0f}")
        print(f"  Fair Value: ${score['fair_market_value']:,.0f} | Diff: ${score['price_difference']:,.0f} ({score['price_difference_pct']:+.1f}%)")
        print(f"\n  TOTAL SCORE: {score['total_score']}/100")
        print(f"  Deal Quality: {score['deal_quality']}")
        print(f"  Recommendation: {score['recommendation']}")

        print(f"\n  Score Breakdown:")
        for category, value in score['scores_breakdown'].items():
            print(f"    {category.capitalize():<15}: {value:>5.1f}/100")

        print(f"\n  Location: {listing.get('city', 'N/A')}, {listing.get('region', 'N/A')}")
        print("-" * 80)

    print("\n" + "=" * 80)
    print("SCORING COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
