"""
Scenario Builder - Creates specific ownership scenarios to analyze
"""

from vehicle_optimizer import Vehicle, OwnershipScenario
from vehicle_database import (
    get_all_vehicles,
    TRAILER_DATABASE,
    BAY_AREA_COSTS
)


def estimate_tesla_trade_in(months_from_now: int) -> float:
    """
    Estimate Tesla Model Y trade-in value
    Based on current market: $35k purchase, 42k miles
    Depreciation accelerates with high mileage
    """
    current_value = 35000
    monthly_miles = 1667  # 20k/year pace

    # Tesla depreciation is steep right now
    base_monthly_depreciation = 0.015  # 1.5% per month

    # Additional mileage penalty when crossing thresholds
    future_miles = 42000 + (monthly_miles * months_from_now)

    if future_miles > 50000:
        # Out of warranty territory, steeper depreciation
        base_monthly_depreciation = 0.020

    future_value = current_value * ((1 - base_monthly_depreciation) ** months_from_now)

    # Trade-in typically 10-15% below private party
    trade_in_value = future_value * 0.87

    return round(trade_in_value, 2)


def calculate_credits_earned(months_from_june_2025: int) -> float:
    """
    Calculate total credits earned based on time from June 2025

    PG&E: $4,000 pro-rated over 20 months ($200/month)
    3CE: $2,000 (vests after 12 months)

    months_from_june_2025: Number of months since June 2025
    """
    # PG&E credit: $200/month for up to 20 months
    pge_months = min(months_from_june_2025, 20)
    pge_credit = pge_months * 200

    # 3CE credit: $2,000 if held for 12+ months
    ce_credit = 2000 if months_from_june_2025 >= 12 else 0

    total = pge_credit + ce_credit

    return total


def build_scenario_1_keep_tesla_5_months() -> OwnershipScenario:
    """
    Scenario 1: Keep Tesla for 5 more months (to June 2026) to unlock 3CE credit
    Currently at month 7 (Jan 2026), need to reach month 12 (June 2026)
    """
    vehicles = get_all_vehicles()

    # Credits earned if kept to June 2026 (month 12 from June 2025)
    credits_at_june = calculate_credits_earned(12)  # $2,400 PG&E + $2,000 3CE = $4,400

    return OwnershipScenario(
        name="Keep Tesla to June 2026 (Unlock 3CE)",
        vehicles=[vehicles['tesla_model_y']],
        months_to_analyze=5,  # 5 more months from now to June
        annual_mileage=20000,
        pending_credits=credits_at_june,
        months_until_credits=5,
        trade_in_value=0,  # Not trading in anything
        storage_cost_monthly=0
    )


def build_scenario_2_sell_now_tacoma() -> OwnershipScenario:
    """
    Scenario 2: Sell Tesla now, buy new Tacoma
    Credits earned: Currently at month 7, so $1,400 PG&E only
    """
    vehicles = get_all_vehicles()
    tacoma = vehicles['tacoma']

    # Credits if sold now (month 7): $1,400 PG&E, forfeit $2,600 PG&E + $2,000 3CE
    credits_now = calculate_credits_earned(7)  # $1,400

    return OwnershipScenario(
        name="Sell Now → New Tacoma",
        vehicles=[tacoma],
        months_to_analyze=36,
        annual_mileage=20000,
        pending_credits=credits_now,
        months_until_credits=0,
        trade_in_value=estimate_tesla_trade_in(0),
        sales_tax_rate=BAY_AREA_COSTS['sales_tax_rate'],
        storage_cost_monthly=0
    )


def build_scenario_3_sell_now_lexus_gx() -> OwnershipScenario:
    """
    Scenario 3: Sell Tesla now, buy new Lexus GX 550
    """
    vehicles = get_all_vehicles()
    credits_now = calculate_credits_earned(7)  # $1,400

    return OwnershipScenario(
        name="Sell Now → New Lexus GX 550",
        vehicles=[vehicles['lexus_gx']],
        months_to_analyze=36,
        annual_mileage=20000,
        pending_credits=credits_now,
        months_until_credits=0,
        trade_in_value=estimate_tesla_trade_in(0),
        sales_tax_rate=BAY_AREA_COSTS['sales_tax_rate'],
        storage_cost_monthly=0
    )


def build_scenario_4_sell_now_lexus_lx() -> OwnershipScenario:
    """
    Scenario 4: Sell Tesla now, buy Lexus LX 600
    """
    vehicles = get_all_vehicles()

    return OwnershipScenario(
        name="Sell Now → Lexus LX",
        vehicles=[vehicles['lexus_lx']],
        months_to_analyze=36,
        annual_mileage=20000,
        pending_credits=0,
        months_until_credits=0,
        trade_in_value=estimate_tesla_trade_in(0),
        sales_tax_rate=BAY_AREA_COSTS['sales_tax_rate'],
        storage_cost_monthly=0
    )


def build_scenario_5_sell_now_escalade() -> OwnershipScenario:
    """
    Scenario 5: Sell Tesla now, buy Escalade
    """
    vehicles = get_all_vehicles()

    return OwnershipScenario(
        name="Sell Now → Escalade",
        vehicles=[vehicles['escalade']],
        months_to_analyze=36,
        annual_mileage=20000,
        pending_credits=0,
        months_until_credits=0,
        trade_in_value=estimate_tesla_trade_in(0),
        sales_tax_rate=BAY_AREA_COSTS['sales_tax_rate'],
        storage_cost_monthly=0
    )


def build_scenario_6_sell_now_f150() -> OwnershipScenario:
    """
    Scenario 6: Sell Tesla now, buy Ford F-150
    """
    vehicles = get_all_vehicles()

    return OwnershipScenario(
        name="Sell Now → F-150",
        vehicles=[vehicles['f150']],
        months_to_analyze=36,
        annual_mileage=20000,
        pending_credits=0,
        months_until_credits=0,
        trade_in_value=estimate_tesla_trade_in(0),
        sales_tax_rate=BAY_AREA_COSTS['sales_tax_rate'],
        storage_cost_monthly=0
    )


def build_scenario_7_sell_now_4runner() -> OwnershipScenario:
    """
    Scenario 7: Sell Tesla now, buy 4Runner (user's history)
    """
    vehicles = get_all_vehicles()

    return OwnershipScenario(
        name="Sell Now → 4Runner",
        vehicles=[vehicles['4runner']],
        months_to_analyze=36,
        annual_mileage=20000,
        pending_credits=0,
        months_until_credits=0,
        trade_in_value=estimate_tesla_trade_in(0),
        sales_tax_rate=BAY_AREA_COSTS['sales_tax_rate'],
        storage_cost_monthly=0
    )


def build_scenario_8_sell_now_tacoma_with_trailer() -> OwnershipScenario:
    """
    Scenario 8: Sell Tesla now, buy Tacoma + A-Liner trailer
    """
    vehicles = get_all_vehicles()
    trailer = TRAILER_DATABASE['a_liner_classic']

    return OwnershipScenario(
        name="Sell Now → Tacoma + A-Liner Trailer",
        vehicles=[vehicles['tacoma']],
        months_to_analyze=36,
        annual_mileage=20000,
        pending_credits=0,
        months_until_credits=0,
        trade_in_value=estimate_tesla_trade_in(0),
        sales_tax_rate=BAY_AREA_COSTS['sales_tax_rate'],
        trailer_cost=trailer['cost'],
        trailer_depreciation_annual=trailer['annual_depreciation'],
        storage_cost_monthly=0  # Can store at home
    )


def build_scenario_9_keep_tesla_buy_used_truck() -> OwnershipScenario:
    """
    Scenario 9: Keep Tesla + buy used truck for adventures (dual vehicle)
    Storage cost applies
    """
    vehicles_db = get_all_vehicles()

    # Create a used, cheaper truck for secondary use
    used_tacoma = Vehicle(
        name="2018 Toyota Tacoma TRD (Used)",
        make="Toyota",
        model="Tacoma TRD",
        year=2018,
        purchase_price=32000,
        current_mileage=60000,
        msrp=40000,
        cargo_capacity_cuft=61,
        towing_capacity_lbs=6400,
        mpg_city=18,
        mpg_highway=23,
        fuel_type="gasoline",
        legroom_front_in=42.9,
        legroom_rear_in=34.6,
        ride_comfort_score=6.5,
        roof_rack_capable=True,
        awd_4wd=True,
        insurance_annual=1200,
        registration_annual=450,
        maintenance_per_mile=0.10,
        brand_reliability_score=9.5,
        market_demand_score=9.0
    )

    return OwnershipScenario(
        name="Keep Tesla + Used Tacoma (Dual)",
        vehicles=[vehicles_db['tesla_model_y'], used_tacoma],
        months_to_analyze=36,
        annual_mileage=15000,  # Split between vehicles
        pending_credits=6000,
        months_until_credits=6,
        trade_in_value=0,
        sales_tax_rate=BAY_AREA_COSTS['sales_tax_rate'],
        storage_cost_monthly=BAY_AREA_COSTS['storage_unit_monthly']  # Store truck
    )


def build_scenario_10_wait_june_then_new_gx() -> OwnershipScenario:
    """
    Scenario 10: Wait to June 2026 (5mo, unlock 3CE), then buy new Lexus GX 550
    """
    vehicles = get_all_vehicles()
    credits_june = calculate_credits_earned(12)  # $4,400

    return OwnershipScenario(
        name="Wait June → New Lexus GX 550",
        vehicles=[vehicles['lexus_gx']],
        months_to_analyze=36,
        annual_mileage=20000,
        pending_credits=credits_june,
        months_until_credits=5,  # 5 months from now to June
        trade_in_value=estimate_tesla_trade_in(5),
        sales_tax_rate=BAY_AREA_COSTS['sales_tax_rate'],
        storage_cost_monthly=0
    )


def build_scenario_11_sell_now_gx_with_trailer() -> OwnershipScenario:
    """
    Scenario 11: Sell Tesla now, buy Lexus GX + Taxa Mantis trailer
    Ultimate adventure setup
    """
    vehicles = get_all_vehicles()
    trailer = TRAILER_DATABASE['taxa_mantis']

    return OwnershipScenario(
        name="Sell Now → Lexus GX + Taxa Mantis",
        vehicles=[vehicles['lexus_gx']],
        months_to_analyze=36,
        annual_mileage=20000,
        pending_credits=0,
        months_until_credits=0,
        trade_in_value=estimate_tesla_trade_in(0),
        sales_tax_rate=BAY_AREA_COSTS['sales_tax_rate'],
        trailer_cost=trailer['cost'],
        trailer_depreciation_annual=trailer['annual_depreciation'],
        storage_cost_monthly=100  # Partial storage for trailer
    )


def build_scenario_12_sell_now_used_tacoma() -> OwnershipScenario:
    """
    Scenario 12: Sell Tesla now, buy used 2022 Tacoma
    Lower initial cost, slightly higher maintenance
    """
    vehicles = get_all_vehicles()
    credits_now = calculate_credits_earned(7)  # $1,400

    return OwnershipScenario(
        name="Sell Now → Used Tacoma (2022)",
        vehicles=[vehicles['used_tacoma']],
        months_to_analyze=36,
        annual_mileage=20000,
        pending_credits=credits_now,
        months_until_credits=0,
        trade_in_value=estimate_tesla_trade_in(0),
        sales_tax_rate=BAY_AREA_COSTS['sales_tax_rate'],
        storage_cost_monthly=0
    )


def build_scenario_13_sell_now_used_gx() -> OwnershipScenario:
    """
    Scenario 13: Sell Tesla now, buy used 2021 Lexus GX 460
    Lower initial cost than new GX 550, proven reliability
    """
    vehicles = get_all_vehicles()
    credits_now = calculate_credits_earned(7)  # $1,400

    return OwnershipScenario(
        name="Sell Now → Used GX 460 (2021)",
        vehicles=[vehicles['used_lexus_gx']],
        months_to_analyze=36,
        annual_mileage=20000,
        pending_credits=credits_now,
        months_until_credits=0,
        trade_in_value=estimate_tesla_trade_in(0),
        sales_tax_rate=BAY_AREA_COSTS['sales_tax_rate'],
        storage_cost_monthly=0
    )


def build_scenario_14_wait_june_used_tacoma() -> OwnershipScenario:
    """
    Scenario 14: Wait to June 2026, then buy used Tacoma
    Best of both: unlock 3CE credit + lower vehicle cost
    """
    vehicles = get_all_vehicles()
    credits_june = calculate_credits_earned(12)  # $4,400

    return OwnershipScenario(
        name="Wait June → Used Tacoma (2022)",
        vehicles=[vehicles['used_tacoma']],
        months_to_analyze=36,
        annual_mileage=20000,
        pending_credits=credits_june,
        months_until_credits=5,
        trade_in_value=estimate_tesla_trade_in(5),
        sales_tax_rate=BAY_AREA_COSTS['sales_tax_rate'],
        storage_cost_monthly=0
    )


def build_scenario_15_wait_june_used_gx() -> OwnershipScenario:
    """
    Scenario 15: Wait to June 2026, then buy used GX 460
    Premium comfort at lower initial cost
    """
    vehicles = get_all_vehicles()
    credits_june = calculate_credits_earned(12)  # $4,400

    return OwnershipScenario(
        name="Wait June → Used GX 460 (2021)",
        vehicles=[vehicles['used_lexus_gx']],
        months_to_analyze=36,
        annual_mileage=20000,
        pending_credits=credits_june,
        months_until_credits=5,
        trade_in_value=estimate_tesla_trade_in(5),
        sales_tax_rate=BAY_AREA_COSTS['sales_tax_rate'],
        storage_cost_monthly=0
    )


def build_scenario_16_sell_now_sequoia() -> OwnershipScenario:
    """
    Scenario 16: Sell Tesla now, buy Toyota Sequoia
    Best for tall drivers needing max space
    """
    vehicles = get_all_vehicles()
    credits_now = calculate_credits_earned(7)  # $1,400

    return OwnershipScenario(
        name="Sell Now → Sequoia",
        vehicles=[vehicles['sequoia']],
        months_to_analyze=36,
        annual_mileage=20000,
        pending_credits=credits_now,
        months_until_credits=0,
        trade_in_value=estimate_tesla_trade_in(0),
        sales_tax_rate=BAY_AREA_COSTS['sales_tax_rate'],
        storage_cost_monthly=0
    )


def build_scenario_17_sell_now_tundra() -> OwnershipScenario:
    """
    Scenario 17: Sell Tesla now, buy Toyota Tundra
    Best towing, excellent legroom for tall drivers
    """
    vehicles = get_all_vehicles()
    credits_now = calculate_credits_earned(7)  # $1,400

    return OwnershipScenario(
        name="Sell Now → Tundra",
        vehicles=[vehicles['tundra']],
        months_to_analyze=36,
        annual_mileage=20000,
        pending_credits=credits_now,
        months_until_credits=0,
        trade_in_value=estimate_tesla_trade_in(0),
        sales_tax_rate=BAY_AREA_COSTS['sales_tax_rate'],
        storage_cost_monthly=0
    )


def build_scenario_18_wait_june_sequoia() -> OwnershipScenario:
    """
    Scenario 18: Wait to June 2026, then buy Sequoia
    Max credits + best full-size SUV for tall drivers
    """
    vehicles = get_all_vehicles()
    credits_june = calculate_credits_earned(12)  # $4,400

    return OwnershipScenario(
        name="Wait June → Sequoia",
        vehicles=[vehicles['sequoia']],
        months_to_analyze=36,
        annual_mileage=20000,
        pending_credits=credits_june,
        months_until_credits=5,
        trade_in_value=estimate_tesla_trade_in(5),
        sales_tax_rate=BAY_AREA_COSTS['sales_tax_rate'],
        storage_cost_monthly=0
    )


def build_scenario_19_wait_june_tundra() -> OwnershipScenario:
    """
    Scenario 19: Wait to June 2026, then buy Tundra
    Max credits + best towing + great fit for 6'3" driver
    """
    vehicles = get_all_vehicles()
    credits_june = calculate_credits_earned(12)  # $4,400

    return OwnershipScenario(
        name="Wait June → Tundra",
        vehicles=[vehicles['tundra']],
        months_to_analyze=36,
        annual_mileage=20000,
        pending_credits=credits_june,
        months_until_credits=5,
        trade_in_value=estimate_tesla_trade_in(5),
        sales_tax_rate=BAY_AREA_COSTS['sales_tax_rate'],
        storage_cost_monthly=0
    )


def build_all_scenarios() -> list:
    """Build all scenarios for comparison - Updated with correct credits and used options"""
    return [
        build_scenario_1_keep_tesla_5_months(),
        build_scenario_2_sell_now_tacoma(),
        build_scenario_12_sell_now_used_tacoma(),  # NEW: Used Tacoma comparison
        build_scenario_14_wait_june_used_tacoma(),  # NEW: Wait + Used Tacoma
        build_scenario_3_sell_now_lexus_gx(),
        build_scenario_13_sell_now_used_gx(),  # NEW: Used GX comparison
        build_scenario_15_wait_june_used_gx(),  # NEW: Wait + Used GX
        build_scenario_4_sell_now_lexus_lx(),
        build_scenario_5_sell_now_escalade(),
        build_scenario_6_sell_now_f150(),
        build_scenario_7_sell_now_4runner(),
        build_scenario_8_sell_now_tacoma_with_trailer(),
        build_scenario_9_keep_tesla_buy_used_truck(),
        build_scenario_10_wait_june_then_new_gx(),
        build_scenario_11_sell_now_gx_with_trailer(),
        build_scenario_16_sell_now_sequoia(),  # NEW: Sequoia
        build_scenario_17_sell_now_tundra(),    # NEW: Tundra
        build_scenario_18_wait_june_sequoia(),  # NEW: Wait + Sequoia
        build_scenario_19_wait_june_tundra()    # NEW: Wait + Tundra
    ]


def get_user_priorities() -> dict:
    """
    User's feature priorities based on their needs
    USER: 6'3" tall, needs back comfort, off-road capability
    Weights must sum to 1.0
    """
    return {
        'legroom': 0.25,  # CRITICAL - 6'3" tall, need excellent legroom (42"+ front)
        'comfort': 0.20,  # CRITICAL - back health, need good ride quality
        'outdoor': 0.20,  # High priority - towing, roof rack, AWD, off-road
        'cargo': 0.15,   # Important for mountain biking, surfing, camping
        'range': 0.10,   # Useful for long trips
        'cost_efficiency': 0.10  # Considered but not primary concern
    }
