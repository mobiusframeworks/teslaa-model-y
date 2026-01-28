"""
Vehicle Optimization System
Analyzes vehicle ownership scenarios based on depreciation, costs, and functionality
"""

import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import math


@dataclass
class Vehicle:
    """Vehicle specification and pricing data"""
    name: str
    make: str
    model: str
    year: int
    purchase_price: float
    current_mileage: int
    msrp: Optional[float] = None

    # Specifications
    cargo_capacity_cuft: float = 0
    towing_capacity_lbs: int = 0
    mpg_city: float = 0
    mpg_highway: float = 0
    mpge: float = 0  # For electric vehicles
    fuel_type: str = "gasoline"

    # Comfort & Features
    legroom_front_in: float = 0
    legroom_rear_in: float = 0
    ride_comfort_score: float = 0  # 1-10 scale
    roof_rack_capable: bool = False
    awd_4wd: bool = False

    # Ownership costs
    insurance_annual: float = 0
    registration_annual: float = 0
    maintenance_per_mile: float = 0

    # Depreciation factors
    brand_reliability_score: float = 0  # 1-10, affects depreciation
    market_demand_score: float = 0  # 1-10, affects depreciation


@dataclass
class OwnershipScenario:
    """Represents a specific vehicle ownership scenario"""
    name: str
    vehicles: List[Vehicle]

    # Current state
    months_to_analyze: int = 36
    annual_mileage: int = 20000

    # Credits and incentives
    pending_credits: float = 0
    months_until_credits: int = 0

    # Initial transaction costs
    trade_in_value: float = 0
    sales_tax_rate: float = 0.0825  # Bay Area avg
    registration_fee: float = 500
    transfer_fee: float = 85

    # Additional equipment
    trailer_cost: float = 0
    trailer_depreciation_annual: float = 0
    storage_cost_monthly: float = 0

    # Calculated fields
    total_cost_of_ownership: float = field(init=False, default=0)
    functionality_score: float = field(init=False, default=0)


class DepreciationModel:
    """Calculates vehicle depreciation over time"""

    @staticmethod
    def calculate_depreciation_rate(vehicle: Vehicle, age_years: int, mileage: int) -> float:
        """
        Calculate annual depreciation rate based on multiple factors
        Returns depreciation multiplier (e.g., 0.15 = 15% per year)
        """
        base_rate = 0.15  # Base 15% annual depreciation

        # Age factor: Depreciation slows over time
        if age_years <= 1:
            age_multiplier = 1.5  # First year hits hardest
        elif age_years <= 3:
            age_multiplier = 1.2
        elif age_years <= 5:
            age_multiplier = 1.0
        else:
            age_multiplier = 0.7  # Slows down after 5 years

        # Mileage factor
        avg_miles_per_year = 12000
        miles_per_year = mileage / max(age_years, 1)
        if miles_per_year > avg_miles_per_year * 1.5:
            mileage_multiplier = 1.3  # High mileage increases depreciation
        elif miles_per_year > avg_miles_per_year:
            mileage_multiplier = 1.1
        else:
            mileage_multiplier = 1.0

        # Brand reliability factor (higher = slower depreciation)
        reliability_multiplier = 1.2 - (vehicle.brand_reliability_score / 50)

        # Market demand factor (higher = slower depreciation)
        demand_multiplier = 1.15 - (vehicle.market_demand_score / 50)

        # Electric vehicle factor (higher depreciation for EVs currently)
        ev_multiplier = 1.25 if vehicle.fuel_type == "electric" else 1.0

        total_rate = (base_rate * age_multiplier * mileage_multiplier *
                     reliability_multiplier * demand_multiplier * ev_multiplier)

        return min(total_rate, 0.40)  # Cap at 40% annual depreciation

    @staticmethod
    def project_value(vehicle: Vehicle, months_forward: int, additional_mileage: int) -> List[Dict]:
        """
        Project vehicle value over time
        Returns list of monthly projections
        """
        projections = []
        current_value = vehicle.purchase_price
        current_age = datetime.now().year - vehicle.year
        current_mileage = vehicle.current_mileage

        for month in range(months_forward + 1):
            age_years = current_age + (month / 12)
            mileage = current_mileage + (additional_mileage * month / 12)

            if month > 0:
                # Apply monthly depreciation
                annual_rate = DepreciationModel.calculate_depreciation_rate(
                    vehicle, int(age_years), int(mileage)
                )
                monthly_rate = annual_rate / 12
                current_value *= (1 - monthly_rate)

            projections.append({
                'month': month,
                'value': round(current_value, 2),
                'age_years': round(age_years, 2),
                'mileage': int(mileage),
                'depreciation_rate_annual': round(
                    DepreciationModel.calculate_depreciation_rate(
                        vehicle, int(age_years), int(mileage)
                    ) * 100, 2
                )
            })

        return projections


class FunctionalityScorer:
    """Scores vehicles based on user needs"""

    def __init__(self, user_priorities: Dict[str, float]):
        """
        user_priorities: Dict of feature: weight (0-1)
        Weights should sum to 1.0
        """
        self.priorities = user_priorities

    def score_vehicle(self, vehicle: Vehicle, has_trailer: bool = False) -> Dict:
        """Calculate weighted functionality score"""
        scores = {}

        # Cargo capacity (normalize to 0-10 scale)
        total_cargo = vehicle.cargo_capacity_cuft
        if has_trailer:
            total_cargo += 100  # A-frame trailer adds ~100 cu ft
        scores['cargo'] = min(total_cargo / 15, 10)  # 150+ cu ft = perfect score

        # Legroom comfort (based on hip problems)
        avg_legroom = (vehicle.legroom_front_in + vehicle.legroom_rear_in) / 2
        scores['legroom'] = min(avg_legroom / 4.2, 10)  # 42+ inches = perfect

        # Overall comfort
        scores['comfort'] = vehicle.ride_comfort_score

        # Outdoor capability
        outdoor_score = 0
        if vehicle.roof_rack_capable:
            outdoor_score += 3
        if vehicle.awd_4wd:
            outdoor_score += 3
        if vehicle.towing_capacity_lbs >= 3500:
            outdoor_score += 4
        elif vehicle.towing_capacity_lbs >= 2000:
            outdoor_score += 2
        scores['outdoor'] = outdoor_score

        # Long-distance travel (range/efficiency)
        if vehicle.fuel_type == "electric":
            # Assume ~300 mile range for Model Y
            range_score = 5 if vehicle.mpge > 100 else 3
        else:
            # Calculate range based on typical tank size
            tank_size = 20 if "truck" in vehicle.model.lower() else 16
            range_miles = tank_size * vehicle.mpg_highway
            range_score = min(range_miles / 50, 10)
        scores['range'] = range_score

        # Cost efficiency (inverse of operating cost per mile)
        if vehicle.fuel_type == "electric":
            cost_per_mile = 0.04  # ~$0.04/mile for electricity
        else:
            cost_per_mile = 3.5 / vehicle.mpg_highway  # Assume $3.50/gal
        cost_per_mile += vehicle.maintenance_per_mile
        scores['cost_efficiency'] = max(10 - (cost_per_mile * 100), 0)

        # Calculate weighted total
        weighted_score = sum(
            scores.get(feature, 0) * weight
            for feature, weight in self.priorities.items()
        )

        return {
            'total_score': round(weighted_score, 2),
            'breakdown': {k: round(v, 2) for k, v in scores.items()}
        }


class CostCalculator:
    """Calculates total cost of ownership"""

    @staticmethod
    def calculate_acquisition_cost(scenario: OwnershipScenario) -> Dict:
        """Calculate upfront costs to acquire vehicles"""
        costs = {}

        total_purchase = sum(v.purchase_price for v in scenario.vehicles)
        costs['purchase_price'] = total_purchase
        costs['trade_in_credit'] = -scenario.trade_in_value
        costs['sales_tax'] = (total_purchase - scenario.trade_in_value) * scenario.sales_tax_rate
        costs['registration'] = scenario.registration_fee * len(scenario.vehicles)
        costs['transfer_fees'] = scenario.transfer_fee * len(scenario.vehicles)
        costs['trailer'] = scenario.trailer_cost

        costs['total_acquisition'] = sum(costs.values())

        return costs

    @staticmethod
    def calculate_operating_costs(scenario: OwnershipScenario) -> Dict:
        """Calculate ongoing operating costs over analysis period"""
        months = scenario.months_to_analyze
        years = months / 12
        annual_miles = scenario.annual_mileage

        costs = {}

        # Per-vehicle costs
        for i, vehicle in enumerate(scenario.vehicles):
            prefix = f"vehicle_{i+1}"

            # Fuel/electricity
            miles = annual_miles * years
            if vehicle.fuel_type == "electric":
                fuel_cost = miles * 0.04  # $0.04/mile for electricity
            else:
                mpg = (vehicle.mpg_city + vehicle.mpg_highway) / 2
                gallons = miles / mpg
                fuel_cost = gallons * 3.50  # $3.50/gal average
            costs[f'{prefix}_fuel'] = fuel_cost

            # Insurance
            costs[f'{prefix}_insurance'] = vehicle.insurance_annual * years

            # Registration
            costs[f'{prefix}_registration'] = vehicle.registration_annual * years

            # Maintenance
            costs[f'{prefix}_maintenance'] = miles * vehicle.maintenance_per_mile

        # Storage costs
        if scenario.storage_cost_monthly > 0:
            costs['storage'] = scenario.storage_cost_monthly * months

        # Trailer depreciation
        if scenario.trailer_cost > 0:
            costs['trailer_depreciation'] = scenario.trailer_depreciation_annual * years

        costs['total_operating'] = sum(costs.values())

        return costs

    @staticmethod
    def calculate_net_position(scenario: OwnershipScenario) -> Dict:
        """Calculate net financial position after analysis period"""
        # Acquisition costs
        acquisition = CostCalculator.calculate_acquisition_cost(scenario)

        # Operating costs
        operating = CostCalculator.calculate_operating_costs(scenario)

        # Future vehicle values
        future_values = {}
        total_future_value = 0

        for i, vehicle in enumerate(scenario.vehicles):
            projections = DepreciationModel.project_value(
                vehicle,
                scenario.months_to_analyze,
                scenario.annual_mileage
            )
            final_value = projections[-1]['value']
            future_values[f'vehicle_{i+1}_value'] = final_value
            total_future_value += final_value

        # Credits
        credits = scenario.pending_credits if scenario.months_to_analyze >= scenario.months_until_credits else 0

        # Net calculation
        total_costs = acquisition['total_acquisition'] + operating['total_operating']
        net_position = total_future_value + credits - total_costs

        return {
            'acquisition_costs': acquisition,
            'operating_costs': operating,
            'future_values': future_values,
            'total_future_value': total_future_value,
            'credits': credits,
            'total_costs': total_costs,
            'net_position': net_position,
            'equivalent_monthly_cost': -net_position / scenario.months_to_analyze
        }


class ScenarioAnalyzer:
    """Analyzes and compares multiple scenarios"""

    def __init__(self, user_priorities: Dict[str, float]):
        self.scorer = FunctionalityScorer(user_priorities)

    def analyze_scenario(self, scenario: OwnershipScenario) -> Dict:
        """Complete analysis of a single scenario"""
        # Financial analysis
        financial = CostCalculator.calculate_net_position(scenario)

        # Functionality scoring
        functionality_scores = []
        for i, vehicle in enumerate(scenario.vehicles):
            has_trailer = scenario.trailer_cost > 0
            score_data = self.scorer.score_vehicle(vehicle, has_trailer)
            functionality_scores.append({
                f'vehicle_{i+1}': vehicle.name,
                **score_data
            })

        # Combined functionality score (average if multiple vehicles)
        avg_functionality = sum(s['total_score'] for s in functionality_scores) / len(functionality_scores)

        # Depreciation projections
        depreciation_analysis = []
        for vehicle in scenario.vehicles:
            projections = DepreciationModel.project_value(
                vehicle,
                scenario.months_to_analyze,
                scenario.annual_mileage
            )
            depreciation_analysis.append({
                'vehicle': vehicle.name,
                'current_value': vehicle.purchase_price,
                'future_value': projections[-1]['value'],
                'total_depreciation': vehicle.purchase_price - projections[-1]['value'],
                'projections': projections
            })

        return {
            'scenario_name': scenario.name,
            'financial_summary': financial,
            'functionality_score': round(avg_functionality, 2),
            'functionality_details': functionality_scores,
            'depreciation_analysis': depreciation_analysis,
            'recommendation_score': self._calculate_recommendation_score(
                financial['net_position'],
                avg_functionality
            )
        }

    def _calculate_recommendation_score(self, net_position: float, functionality: float) -> float:
        """
        Calculate overall recommendation score combining financial and functional aspects
        Higher is better
        """
        # Normalize financial position to 0-10 scale
        # Assume range of -30000 to +10000
        financial_score = ((net_position + 30000) / 40000) * 10
        financial_score = max(0, min(10, financial_score))

        # Weight: 40% financial, 60% functionality (since user prioritizes functionality)
        overall = (financial_score * 0.4) + (functionality * 0.6)

        return round(overall, 2)

    def compare_scenarios(self, scenarios: List[OwnershipScenario]) -> Dict:
        """Compare multiple scenarios and rank them"""
        analyses = [self.analyze_scenario(s) for s in scenarios]

        # Rank by recommendation score
        ranked = sorted(analyses, key=lambda x: x['recommendation_score'], reverse=True)

        return {
            'analyses': analyses,
            'ranked': ranked,
            'best_scenario': ranked[0]['scenario_name'],
            'comparison_summary': self._create_comparison_table(ranked)
        }

    def _create_comparison_table(self, ranked_analyses: List[Dict]) -> List[Dict]:
        """Create simplified comparison table"""
        comparison = []

        for analysis in ranked_analyses:
            comparison.append({
                'scenario': analysis['scenario_name'],
                'recommendation_score': analysis['recommendation_score'],
                'functionality_score': analysis['functionality_score'],
                'net_position': round(analysis['financial_summary']['net_position'], 2),
                'monthly_cost': round(analysis['financial_summary']['equivalent_monthly_cost'], 2),
                'total_costs': round(analysis['financial_summary']['total_costs'], 2)
            })

        return comparison


def main():
    """Main execution function"""
    print("Vehicle Optimization System - Initializing...")
    print("=" * 80)


if __name__ == "__main__":
    main()
