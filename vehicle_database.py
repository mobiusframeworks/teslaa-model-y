"""
Vehicle Database with Real Specifications and Bay Area Pricing
"""

from vehicle_optimizer import Vehicle


def create_tesla_model_y_2024() -> Vehicle:
    """Current vehicle: 2024 Tesla Model Y AWD Long Range"""
    return Vehicle(
        name="2024 Tesla Model Y AWD LR (Current)",
        make="Tesla",
        model="Model Y Long Range",
        year=2024,
        purchase_price=35000,  # What user paid
        current_mileage=42000,
        msrp=48990,

        # Specifications
        cargo_capacity_cuft=76,  # Behind front seats
        towing_capacity_lbs=3500,
        mpg_city=0,
        mpg_highway=0,
        mpge=122,  # Combined EPA rating
        fuel_type="electric",

        # Comfort & Features
        legroom_front_in=41.8,
        legroom_rear_in=40.5,
        ride_comfort_score=7.5,  # Good but firm suspension
        roof_rack_capable=True,
        awd_4wd=True,

        # Ownership costs (Bay Area estimates)
        insurance_annual=1800,
        registration_annual=550,
        maintenance_per_mile=0.05,  # EVs are cheaper to maintain

        # Depreciation factors
        brand_reliability_score=7.0,  # Tesla reliability is mixed
        market_demand_score=6.5  # High supply, depreciation concerns
    )


def create_toyota_tacoma_2025() -> Vehicle:
    """2025 Toyota Tacoma TRD Off-Road"""
    return Vehicle(
        name="2025 Toyota Tacoma TRD Off-Road",
        make="Toyota",
        model="Tacoma TRD Off-Road",
        year=2025,
        purchase_price=48000,  # Bay Area pricing
        current_mileage=0,
        msrp=47995,

        # Specifications
        cargo_capacity_cuft=61,  # Bed + cabin
        towing_capacity_lbs=6500,
        mpg_city=19,
        mpg_highway=24,
        mpge=0,
        fuel_type="gasoline",

        # Comfort & Features
        legroom_front_in=42.9,
        legroom_rear_in=34.6,  # Limited rear space
        ride_comfort_score=6.5,  # Truck ride, can be rough
        roof_rack_capable=True,
        awd_4wd=True,

        # Ownership costs
        insurance_annual=1600,
        registration_annual=650,
        maintenance_per_mile=0.12,

        # Depreciation factors
        brand_reliability_score=9.5,  # Toyota legendary reliability
        market_demand_score=9.0  # High demand, holds value well
    )


def create_lexus_gx_550_2024() -> Vehicle:
    """2024 Lexus GX 550 Premium"""
    return Vehicle(
        name="2024 Lexus GX 550 Premium",
        make="Lexus",
        model="GX 550",
        year=2024,
        purchase_price=68000,  # Used/demo pricing
        current_mileage=5000,
        msrp=67950,

        # Specifications
        cargo_capacity_cuft=91,  # Behind front seats, 120+ with seats down
        towing_capacity_lbs=8000,
        mpg_city=14,
        mpg_highway=19,
        mpge=0,
        fuel_type="gasoline",

        # Comfort & Features
        legroom_front_in=43.6,
        legroom_rear_in=38.4,
        ride_comfort_score=9.0,  # Excellent comfort, luxury SUV
        roof_rack_capable=True,
        awd_4wd=True,

        # Ownership costs
        insurance_annual=2200,
        registration_annual=950,
        maintenance_per_mile=0.15,

        # Depreciation factors
        brand_reliability_score=9.5,  # Lexus = Toyota reliability + luxury
        market_demand_score=8.5  # Strong demand, especially new generation
    )


def create_lexus_lx_600_2024() -> Vehicle:
    """2024 Lexus LX 600"""
    return Vehicle(
        name="2024 Lexus LX 600",
        make="Lexus",
        model="LX 600",
        year=2024,
        purchase_price=98000,  # Used pricing
        current_mileage=8000,
        msrp=97000,

        # Specifications
        cargo_capacity_cuft=95,  # Behind front seats
        towing_capacity_lbs=8000,
        mpg_city=14,
        mpg_highway=18,
        mpge=0,
        fuel_type="gasoline",

        # Comfort & Features
        legroom_front_in=44.0,
        legroom_rear_in=44.1,  # Excellent rear legroom
        ride_comfort_score=9.5,  # Top-tier luxury comfort
        roof_rack_capable=True,
        awd_4wd=True,

        # Ownership costs
        insurance_annual=2800,
        registration_annual=1400,
        maintenance_per_mile=0.18,

        # Depreciation factors
        brand_reliability_score=9.5,
        market_demand_score=8.0  # Limited market, but holds value
    )


def create_escalade_2024() -> Vehicle:
    """2024 Cadillac Escalade"""
    return Vehicle(
        name="2024 Cadillac Escalade",
        make="Cadillac",
        model="Escalade",
        year=2024,
        purchase_price=85000,  # Used pricing
        current_mileage=10000,
        msrp=83000,

        # Specifications
        cargo_capacity_cuft=120,  # Behind front seats
        towing_capacity_lbs=8200,
        mpg_city=14,
        mpg_highway=20,
        mpge=0,
        fuel_type="gasoline",

        # Comfort & Features
        legroom_front_in=44.5,
        legroom_rear_in=42.8,
        ride_comfort_score=9.0,
        roof_rack_capable=True,
        awd_4wd=True,

        # Ownership costs
        insurance_annual=2600,
        registration_annual=1200,
        maintenance_per_mile=0.20,

        # Depreciation factors
        brand_reliability_score=6.5,  # GM reliability concerns
        market_demand_score=7.0  # Good demand but higher depreciation
    )


def create_ford_f150_2024() -> Vehicle:
    """2024 Ford F-150 Lariat 4x4"""
    return Vehicle(
        name="2024 Ford F-150 Lariat 4x4",
        make="Ford",
        model="F-150 Lariat",
        year=2024,
        purchase_price=62000,
        current_mileage=8000,
        msrp=61000,

        # Specifications
        cargo_capacity_cuft=77,  # 5.5' bed + cabin storage
        towing_capacity_lbs=11200,  # Max tow package
        mpg_city=17,
        mpg_highway=23,
        mpge=0,
        fuel_type="gasoline",

        # Comfort & Features
        legroom_front_in=43.9,
        legroom_rear_in=43.6,
        ride_comfort_score=8.0,
        roof_rack_capable=True,
        awd_4wd=True,

        # Ownership costs
        insurance_annual=1900,
        registration_annual=850,
        maintenance_per_mile=0.14,

        # Depreciation factors
        brand_reliability_score=7.5,
        market_demand_score=8.5  # F-150 holds value well, best-seller
    )


def create_toyota_4runner_2024() -> Vehicle:
    """2024 Toyota 4Runner TRD Off-Road (alternative option)"""
    return Vehicle(
        name="2024 Toyota 4Runner TRD Off-Road",
        make="Toyota",
        model="4Runner TRD Off-Road",
        year=2024,
        purchase_price=52000,
        current_mileage=5000,
        msrp=51000,

        # Specifications
        cargo_capacity_cuft=89,  # Behind front seats
        towing_capacity_lbs=5000,
        mpg_city=16,
        mpg_highway=19,
        mpge=0,
        fuel_type="gasoline",

        # Comfort & Features
        legroom_front_in=41.7,
        legroom_rear_in=32.9,
        ride_comfort_score=7.0,
        roof_rack_capable=True,
        awd_4wd=True,

        # Ownership costs
        insurance_annual=1700,
        registration_annual=700,
        maintenance_per_mile=0.11,

        # Depreciation factors
        brand_reliability_score=9.5,
        market_demand_score=9.5  # Legendary value retention
    )


# Trailer Options
TRAILER_DATABASE = {
    'a_liner_classic': {
        'name': 'A-Liner Classic Pop-up',
        'cost': 15000,
        'annual_depreciation': 1200,
        'cargo_capacity_cuft': 100,
        'weight_lbs': 1200,
        'description': 'Lightweight aluminum pop-up, easy to tow'
    },
    'opus_air_off_grid': {
        'name': 'Opus Air Off-Grid',
        'cost': 35000,
        'annual_depreciation': 2500,
        'cargo_capacity_cuft': 120,
        'weight_lbs': 2200,
        'description': 'Inflatable roof tent, solar, off-grid capable'
    },
    'taxa_mantis': {
        'name': 'Taxa Mantis',
        'cost': 45000,
        'annual_depreciation': 3000,
        'cargo_capacity_cuft': 110,
        'weight_lbs': 2700,
        'description': 'Premium off-road trailer, well-built'
    }
}


# Bay Area specific costs
BAY_AREA_COSTS = {
    'sales_tax_rate': 0.0925,  # Average across Bay Area counties
    'gas_price_per_gallon': 4.50,  # Bay Area average
    'electricity_per_kwh': 0.35,  # PG&E peak rate
    'storage_unit_monthly': 250,  # For storing 2nd vehicle/trailer
    'registration_base': 500,
    'transfer_fee': 85
}


def create_used_tacoma_2022() -> Vehicle:
    """2022 Toyota Tacoma TRD Off-Road (Used, ~30k miles)"""
    return Vehicle(
        name="2022 Toyota Tacoma TRD (Used)",
        make="Toyota",
        model="Tacoma TRD Off-Road",
        year=2022,
        purchase_price=39000,  # Used pricing, ~$9k less than new
        current_mileage=30000,
        msrp=45000,  # Original MSRP

        # Specifications (same as new)
        cargo_capacity_cuft=61,
        towing_capacity_lbs=6400,
        mpg_city=19,
        mpg_highway=24,
        mpge=0,
        fuel_type="gasoline",

        # Comfort & Features
        legroom_front_in=42.9,
        legroom_rear_in=34.6,
        ride_comfort_score=6.5,
        roof_rack_capable=True,
        awd_4wd=True,

        # Ownership costs (slightly higher maintenance for used)
        insurance_annual=1400,  # Lower than new
        registration_annual=450,  # Lower than new
        maintenance_per_mile=0.13,  # Slightly higher (out of factory warranty soon)

        # Depreciation factors
        brand_reliability_score=9.5,
        market_demand_score=9.0
    )


def create_used_lexus_gx_2021() -> Vehicle:
    """2021 Lexus GX 460 (Used, ~35k miles) - Previous generation"""
    return Vehicle(
        name="2021 Lexus GX 460 (Used)",
        make="Lexus",
        model="GX 460",
        year=2021,
        purchase_price=52000,  # Used pricing, ~$16k less than new GX 550
        current_mileage=35000,
        msrp=62000,  # Original MSRP

        # Specifications (older V8 vs new turbo 6)
        cargo_capacity_cuft=65,  # Behind 2nd row, less than new GX 550
        towing_capacity_lbs=6500,  # Less than new GX 550's 8000
        mpg_city=13,  # Worse than new (V8)
        mpg_highway=18,
        mpge=0,
        fuel_type="gasoline",

        # Comfort & Features
        legroom_front_in=43.0,
        legroom_rear_in=38.0,
        ride_comfort_score=8.5,  # Still great, but not quite 2024 level
        roof_rack_capable=True,
        awd_4wd=True,

        # Ownership costs
        insurance_annual=1900,  # Lower than new
        registration_annual=700,  # Lower than new
        maintenance_per_mile=0.16,  # Higher (older, out of basic warranty)

        # Depreciation factors
        brand_reliability_score=9.5,  # GX 460 is legendary
        market_demand_score=8.0  # Strong used market
    )


def get_all_vehicles() -> dict:
    """Return dictionary of all available vehicles"""
    return {
        'tesla_model_y': create_tesla_model_y_2024(),
        'tacoma': create_toyota_tacoma_2025(),
        'used_tacoma': create_used_tacoma_2022(),
        'lexus_gx': create_lexus_gx_550_2024(),
        'used_lexus_gx': create_used_lexus_gx_2021(),
        'lexus_lx': create_lexus_lx_600_2024(),
        'escalade': create_escalade_2024(),
        'f150': create_ford_f150_2024(),
        '4runner': create_toyota_4runner_2024()
    }
