"""
Data Import Script
Populates database with initial vehicle data for target vehicles:
- Lexus GX
- Ford F-150 4x4
- Toyota Tacoma 4x4
- Toyota Tundra 4x4
- Toyota Sequoia 4x4
- Tesla Model Y AWD
- Tesla Model 3
"""

from database import (
    DatabaseManager, Vehicle, MarketPrice, VehicleProblem,
    DriverFit, VehicleRepository, MarketPriceRepository,
    ProblemRepository, DriverFitRepository
)
from datetime import datetime


def import_target_vehicles():
    """Import all target vehicles with comprehensive data"""

    db = DatabaseManager()
    vehicle_repo = VehicleRepository(db)
    fit_repo = DriverFitRepository(db)
    problem_repo = ProblemRepository(db)

    vehicles_data = []

    # ========== LEXUS GX ==========
    vehicles_data.append({
        'vehicle': Vehicle(
            make="Lexus",
            model="GX",
            year=2024,
            trim="550 Premium",
            body_style="SUV",
            drivetrain="4WD",
            engine="3.5L Twin-Turbo V6",
            transmission="10-Speed Automatic",
            fuel_type="gasoline",
            horsepower=349,
            torque=479,
            seating_capacity=7,
            cargo_capacity_cuft=91,
            towing_capacity_lbs=8000,
            payload_capacity_lbs=1350,
            mpg_city=14,
            mpg_highway=19,
            mpg_combined=16,
            headroom_front_in=38.3,
            headroom_rear_in=37.8,
            legroom_front_in=43.6,
            legroom_rear_in=38.4,
            shoulder_room_front_in=60.4,
            shoulder_room_rear_in=59.2,
            curb_weight_lbs=5665,
            msrp=67950,
            invoice_price=64500
        ),
        'driver_fit': DriverFit(
            vehicle_id=0,  # Will be set after vehicle creation
            recommended_height_min=60,
            recommended_height_max=78,
            seat_comfort_score=9,
            seat_adjustability_score=9,
            lumbar_support_score=9,
            seat_material_quality=9,
            steering_wheel_adjustability=9,
            pedal_position_score=8,
            visibility_score=8,
            tall_driver_suitable=True,
            tall_driver_notes="Excellent for tall drivers. Generous headroom and legroom. Premium leather seats with extensive adjustment."
        ),
        'problems': [
            VehicleProblem(
                make="Lexus",
                model="GX",
                year_start=2024,
                year_end=2024,
                problem_category="Engine",
                problem_description="New generation - no major issues reported yet. Previous GX 460 (2010-2023) was extremely reliable.",
                severity="minor",
                frequency="rare",
                avg_repair_cost=0,
                source="Consumer Reports, forums"
            ),
            VehicleProblem(
                make="Lexus",
                model="GX",
                year_start=2010,
                year_end=2023,
                problem_category="Transmission",
                problem_description="Older 6-speed transmission occasionally had shift hesitation around 60k-80k miles",
                severity="minor",
                frequency="occasional",
                avg_repair_cost=150,
                source="Owner forums"
            )
        ],
        'good_years': "2024 (new generation), 2014-2023 (proven reliability)",
        'avoid_years': "None - GX is one of most reliable SUVs"
    })

    # ========== FORD F-150 ==========
    vehicles_data.append({
        'vehicle': Vehicle(
            make="Ford",
            model="F-150",
            year=2024,
            trim="Lariat 4x4",
            body_style="Truck",
            drivetrain="4WD",
            engine="3.5L EcoBoost V6",
            transmission="10-Speed Automatic",
            fuel_type="gasoline",
            horsepower=400,
            torque=500,
            seating_capacity=6,
            cargo_capacity_cuft=77,
            towing_capacity_lbs=11200,
            payload_capacity_lbs=1940,
            mpg_city=17,
            mpg_highway=23,
            mpg_combined=19,
            headroom_front_in=40.8,
            headroom_rear_in=40.4,
            legroom_front_in=43.9,
            legroom_rear_in=43.6,
            shoulder_room_front_in=66.7,
            shoulder_room_rear_in=66.0,
            curb_weight_lbs=5200,
            msrp=61000,
            invoice_price=58000
        ),
        'driver_fit': DriverFit(
            vehicle_id=0,
            recommended_height_min=62,
            recommended_height_max=78,
            seat_comfort_score=8,
            seat_adjustability_score=8,
            lumbar_support_score=7,
            seat_material_quality=7,
            steering_wheel_adjustability=8,
            pedal_position_score=8,
            visibility_score=9,
            tall_driver_suitable=True,
            tall_driver_notes="Excellent legroom and headroom. High seating position great for tall drivers. Lariat has good seat comfort."
        ),
        'problems': [
            VehicleProblem(
                make="Ford",
                model="F-150",
                year_start=2021,
                year_end=2023,
                problem_category="Engine",
                problem_description="EcoBoost engine: Some reports of cam phaser issues causing rattling noise on cold start",
                severity="moderate",
                frequency="occasional",
                avg_repair_cost=2500,
                source="NHTSA, forums"
            ),
            VehicleProblem(
                make="Ford",
                model="F-150",
                year_start=2021,
                year_end=2022,
                problem_category="Transmission",
                problem_description="10-speed transmission: Occasional harsh shifting or clunking reported",
                severity="minor",
                frequency="occasional",
                avg_repair_cost=1200,
                has_tsb=True,
                tsb_number="21-2139",
                source="TSB database"
            )
        ],
        'good_years': "2018-2020 (proven), 2024 (latest updates)",
        'avoid_years': "2021 (first year issues), 2015 (first year of aluminum body)"
    })

    # ========== TOYOTA TACOMA ==========
    vehicles_data.append({
        'vehicle': Vehicle(
            make="Toyota",
            model="Tacoma",
            year=2024,
            trim="TRD Off-Road 4x4",
            body_style="Truck",
            drivetrain="4WD",
            engine="2.4L Turbo I4",
            transmission="8-Speed Automatic",
            fuel_type="gasoline",
            horsepower=278,
            torque=317,
            seating_capacity=5,
            cargo_capacity_cuft=61,
            towing_capacity_lbs=6500,
            payload_capacity_lbs=1220,
            mpg_city=19,
            mpg_highway=24,
            mpg_combined=21,
            headroom_front_in=39.7,
            headroom_rear_in=37.3,
            legroom_front_in=42.9,
            legroom_rear_in=34.6,
            shoulder_room_front_in=57.6,
            shoulder_room_rear_in=57.6,
            curb_weight_lbs=4600,
            msrp=47995,
            invoice_price=45500
        ),
        'driver_fit': DriverFit(
            vehicle_id=0,
            recommended_height_min=60,
            recommended_height_max=76,
            seat_comfort_score=7,
            seat_adjustability_score=7,
            lumbar_support_score=6,
            seat_material_quality=7,
            steering_wheel_adjustability=7,
            pedal_position_score=7,
            visibility_score=8,
            tall_driver_suitable=True,
            tall_driver_notes="Good front legroom for tall drivers. Rear seat is tight for tall passengers. Seat comfort adequate but not luxury level."
        ),
        'problems': [
            VehicleProblem(
                make="Toyota",
                model="Tacoma",
                year_start=2016,
                year_end=2023,
                problem_category="Transmission",
                problem_description="6-speed automatic: Widespread complaints of slow/hunting shifts, especially 1-2-3 gears",
                severity="moderate",
                frequency="common",
                avg_repair_cost=0,
                notes="Not a mechanical failure, just poor calibration. Toyota has not issued fix.",
                source="Owner forums, Consumer Reports"
            ),
            VehicleProblem(
                make="Toyota",
                model="Tacoma",
                year_start=2016,
                year_end=2020,
                problem_category="Frame",
                problem_description="Frame rust issues in certain regions (salt belt states)",
                severity="major",
                frequency="occasional",
                avg_repair_cost=0,
                has_recall=True,
                recall_number="T-SB-0111-19",
                source="NHTSA"
            ),
            VehicleProblem(
                make="Toyota",
                model="Tacoma",
                year_start=2024,
                year_end=2024,
                problem_category="General",
                problem_description="All-new 2024 model - too new to assess long-term reliability. New turbo engine and 8-speed trans unproven.",
                severity="minor",
                frequency="rare",
                avg_repair_cost=0,
                source="Initial reviews"
            )
        ],
        'good_years': "2020-2023 (mature generation), 2005-2015 (legendary durability)",
        'avoid_years': "2024 (too new, unproven), 2016 (first year issues)"
    })

    # ========== TOYOTA TUNDRA ==========
    vehicles_data.append({
        'vehicle': Vehicle(
            make="Toyota",
            model="Tundra",
            year=2024,
            trim="TRD Pro 4x4",
            body_style="Truck",
            drivetrain="4WD",
            engine="3.5L Twin-Turbo V6 Hybrid",
            transmission="10-Speed Automatic",
            fuel_type="hybrid",
            horsepower=437,
            torque=583,
            seating_capacity=6,
            cargo_capacity_cuft=82,
            towing_capacity_lbs=12000,
            payload_capacity_lbs=1940,
            mpg_city=17,
            mpg_highway=22,
            mpg_combined=19,
            headroom_front_in=40.6,
            headroom_rear_in=39.6,
            legroom_front_in=42.7,
            legroom_rear_in=42.3,
            shoulder_room_front_in=66.7,
            shoulder_room_rear_in=65.9,
            curb_weight_lbs=5800,
            msrp=61000,
            invoice_price=58000
        ),
        'driver_fit': DriverFit(
            vehicle_id=0,
            recommended_height_min=62,
            recommended_height_max=78,
            seat_comfort_score=8,
            seat_adjustability_score=8,
            lumbar_support_score=7,
            seat_material_quality=8,
            steering_wheel_adjustability=8,
            pedal_position_score=8,
            visibility_score=9,
            tall_driver_suitable=True,
            tall_driver_notes="Excellent for tall drivers. CrewMax cab has outstanding rear legroom (42.3in). Front seats comfortable for long drives."
        ),
        'problems': [
            VehicleProblem(
                make="Toyota",
                model="Tundra",
                year_start=2022,
                year_end=2023,
                problem_category="Engine",
                problem_description="New twin-turbo engine: Reports of turbo wastegate rattle, especially when cold",
                severity="minor",
                frequency="occasional",
                avg_repair_cost=0,
                has_tsb=True,
                tsb_number="EG009-23",
                source="TSB database, forums"
            ),
            VehicleProblem(
                make="Toyota",
                model="Tundra",
                year_start=2022,
                year_end=2023,
                problem_category="Electrical",
                problem_description="Infotainment system freezing or crashing, requiring restart",
                severity="minor",
                frequency="occasional",
                avg_repair_cost=0,
                notes="Software updates have improved this",
                source="Owner reports"
            )
        ],
        'good_years': "2007-2021 (rock-solid 5.7L V8), 2024+ (bugs worked out)",
        'avoid_years': "2022 (first year of redesign), 2000-2006 (rust issues)"
    })

    # ========== TOYOTA SEQUOIA ==========
    vehicles_data.append({
        'vehicle': Vehicle(
            make="Toyota",
            model="Sequoia",
            year=2024,
            trim="TRD Pro 4x4",
            body_style="SUV",
            drivetrain="4WD",
            engine="3.5L Twin-Turbo V6 Hybrid",
            transmission="10-Speed Automatic",
            fuel_type="hybrid",
            horsepower=437,
            torque=583,
            seating_capacity=8,
            cargo_capacity_cuft=120,
            towing_capacity_lbs=9300,
            payload_capacity_lbs=1795,
            mpg_city=19,
            mpg_highway=22,
            mpg_combined=20,
            headroom_front_in=39.1,
            headroom_rear_in=38.9,
            legroom_front_in=42.3,
            legroom_rear_in=42.3,
            shoulder_room_front_in=66.0,
            shoulder_room_rear_in=64.4,
            curb_weight_lbs=6290,
            msrp=71000,
            invoice_price=68000
        ),
        'driver_fit': DriverFit(
            vehicle_id=0,
            recommended_height_min=60,
            recommended_height_max=78,
            seat_comfort_score=9,
            seat_adjustability_score=8,
            lumbar_support_score=8,
            seat_material_quality=8,
            steering_wheel_adjustability=8,
            pedal_position_score=8,
            visibility_score=8,
            tall_driver_suitable=True,
            tall_driver_notes="Excellent for tall drivers. Massive rear legroom (42.3in) - can sit tall adults front and back comfortably. Optional captain's chairs are very comfortable."
        ),
        'problems': [
            VehicleProblem(
                make="Toyota",
                model="Sequoia",
                year_start=2023,
                year_end=2024,
                problem_category="Engine",
                problem_description="Same twin-turbo V6 hybrid as Tundra - occasional turbo rattle reported",
                severity="minor",
                frequency="occasional",
                avg_repair_cost=0,
                source="Owner forums"
            ),
            VehicleProblem(
                make="Toyota",
                model="Sequoia",
                year_start=2001,
                year_end=2007,
                problem_category="Frame",
                problem_description="Older generation: Frame rust issues, especially in salt belt states",
                severity="critical",
                frequency="common",
                avg_repair_cost=0,
                has_recall=True,
                notes="Toyota replaced frames under recall",
                source="NHTSA"
            )
        ],
        'good_years': "2024+ (new generation refined), 2008-2022 (extremely reliable 5.7L V8)",
        'avoid_years': "2023 (first year of redesign), 2001-2007 (rust issues)"
    })

    # ========== TESLA MODEL Y ==========
    vehicles_data.append({
        'vehicle': Vehicle(
            make="Tesla",
            model="Model Y",
            year=2024,
            trim="Long Range AWD",
            body_style="SUV",
            drivetrain="AWD",
            engine="Dual Motor Electric",
            transmission="Single-Speed",
            fuel_type="electric",
            horsepower=384,
            torque=376,
            seating_capacity=5,
            cargo_capacity_cuft=76,
            towing_capacity_lbs=3500,
            payload_capacity_lbs=1000,
            mpge=122,
            battery_kwh=75,
            range_miles=310,
            headroom_front_in=41.0,
            headroom_rear_in=39.4,
            legroom_front_in=41.8,
            legroom_rear_in=40.5,
            shoulder_room_front_in=56.4,
            shoulder_room_rear_in=54.0,
            curb_weight_lbs=4555,
            msrp=48990,
            invoice_price=48990
        ),
        'driver_fit': DriverFit(
            vehicle_id=0,
            recommended_height_min=60,
            recommended_height_max=75,
            seat_comfort_score=7,
            seat_adjustability_score=7,
            lumbar_support_score=6,
            seat_material_quality=6,
            steering_wheel_adjustability=7,
            pedal_position_score=7,
            visibility_score=7,
            tall_driver_suitable=True,
            tall_driver_notes="Decent for tall drivers but seats are firm and lack adjustability. Front legroom adequate. Glass roof gives good headroom feel. Seats not great for long drives."
        ),
        'problems': [
            VehicleProblem(
                make="Tesla",
                model="Model Y",
                year_start=2020,
                year_end=2024,
                problem_category="Build Quality",
                problem_description="Panel gaps, misaligned trim, paint defects common on delivery",
                severity="minor",
                frequency="common",
                avg_repair_cost=500,
                notes="Usually covered under warranty if caught early",
                source="Owner forums, Consumer Reports"
            ),
            VehicleProblem(
                make="Tesla",
                model="Model Y",
                year_start=2020,
                year_end=2023,
                problem_category="Suspension",
                problem_description="Rear suspension links failing prematurely (40k-60k miles), causing clunking",
                severity="moderate",
                frequency="occasional",
                avg_repair_cost=1500,
                source="Owner forums, service bulletins"
            ),
            VehicleProblem(
                make="Tesla",
                model="Model Y",
                year_start=2021,
                year_end=2023,
                problem_category="Electrical",
                problem_description="12V battery failures, causing car to become inoperable",
                severity="major",
                frequency="occasional",
                avg_repair_cost=300,
                notes="Tesla now uses lithium 12V battery in newer production",
                source="Owner reports"
            )
        ],
        'good_years': "2024 (refined), 2022 (mid-cycle improvements)",
        'avoid_years': "2020 (first year, many issues)"
    })

    # ========== TESLA MODEL 3 ==========
    vehicles_data.append({
        'vehicle': Vehicle(
            make="Tesla",
            model="Model 3",
            year=2024,
            trim="Long Range AWD",
            body_style="Sedan",
            drivetrain="AWD",
            engine="Dual Motor Electric",
            transmission="Single-Speed",
            fuel_type="electric",
            horsepower=366,
            torque=376,
            seating_capacity=5,
            cargo_capacity_cuft=23,
            towing_capacity_lbs=0,
            payload_capacity_lbs=860,
            mpge=132,
            battery_kwh=75,
            range_miles=341,
            headroom_front_in=40.3,
            headroom_rear_in=37.7,
            legroom_front_in=42.7,
            legroom_rear_in=35.2,
            shoulder_room_front_in=56.3,
            shoulder_room_rear_in=54.0,
            curb_weight_lbs=4048,
            msrp=47740,
            invoice_price=47740
        ),
        'driver_fit': DriverFit(
            vehicle_id=0,
            recommended_height_min=60,
            recommended_height_max=74,
            seat_comfort_score=6,
            seat_adjustability_score=6,
            lumbar_support_score=5,
            seat_material_quality=6,
            steering_wheel_adjustability=6,
            pedal_position_score=6,
            visibility_score=6,
            tall_driver_suitable=False,
            tall_driver_notes="Marginal for tall drivers. Front legroom is OK but seats lack support. Rear legroom very tight. Low roofline can make headroom an issue for 6'3\" and taller. Glass roof helps but seats are uncomfortable for long trips."
        ),
        'problems': [
            VehicleProblem(
                make="Tesla",
                model="Model 3",
                year_start=2018,
                year_end=2023,
                problem_category="Build Quality",
                problem_description="Similar to Model Y: panel gaps, trim issues, paint defects",
                severity="minor",
                frequency="common",
                avg_repair_cost=500,
                source="Consumer Reports, owner forums"
            ),
            VehicleProblem(
                make="Tesla",
                model="Model 3",
                year_start=2018,
                year_end=2022,
                problem_category="Suspension",
                problem_description="Control arm failures causing clunking, especially in cold climates",
                severity="moderate",
                frequency="occasional",
                avg_repair_cost=1200,
                source="Owner reports"
            )
        ],
        'good_years': "2024 (Highland refresh), 2021-2023 (mature production)",
        'avoid_years': "2018 (first year, production hell)"
    })

    # Insert all vehicles
    print("Importing vehicles and data...")
    for item in vehicles_data:
        # Create vehicle
        vehicle_id = vehicle_repo.create_vehicle(item['vehicle'])
        print(f"Created: {item['vehicle'].year} {item['vehicle'].make} {item['vehicle'].model} (ID: {vehicle_id})")

        # Add driver fit data
        fit_data = item['driver_fit']
        fit_data.vehicle_id = vehicle_id
        fit_repo.add_fit_data(fit_data)
        print(f"  - Added driver fit data")

        # Add problems
        for problem in item['problems']:
            problem_repo.add_problem(problem)
        print(f"  - Added {len(item['problems'])} known problems")

        print(f"  - Good years: {item['good_years']}")
        print(f"  - Avoid years: {item['avoid_years']}")
        print()

    print("\n✓ All target vehicles imported successfully!")


def import_sample_market_data():
    """Import sample market pricing data for Bay Area"""

    db = DatabaseManager()
    price_repo = MarketPriceRepository(db)
    vehicle_repo = VehicleRepository(db)

    # Get vehicle IDs
    tacoma_2024 = vehicle_repo.find_vehicles(make="Toyota", model="Tacoma", year_min=2024, year_max=2024)
    gx_2024 = vehicle_repo.find_vehicles(make="Lexus", model="GX", year_min=2024, year_max=2024)
    model_y_2024 = vehicle_repo.find_vehicles(make="Tesla", model="Model Y", year_min=2024, year_max=2024)

    sample_listings = []

    if tacoma_2024:
        tacoma_id = tacoma_2024[0]['id']
        sample_listings.extend([
            MarketPrice(
                vehicle_id=tacoma_id,
                listing_date="2024-01-15",
                mileage=12000,
                asking_price=46500,
                condition="excellent",
                num_owners=1,
                has_tow_package=True,
                city="San Jose",
                region="Bay Area",
                source="Autotrader"
            ),
            MarketPrice(
                vehicle_id=tacoma_id,
                listing_date="2024-01-20",
                mileage=8500,
                asking_price=48000,
                sold=True,
                sale_price=47200,
                sale_date="2024-01-25",
                condition="excellent",
                num_owners=1,
                has_leather=True,
                has_tow_package=True,
                city="Oakland",
                region="Bay Area",
                source="CarMax"
            )
        ])

    if gx_2024:
        gx_id = gx_2024[0]['id']
        sample_listings.extend([
            MarketPrice(
                vehicle_id=gx_id,
                listing_date="2024-01-10",
                mileage=5000,
                asking_price=69500,
                condition="excellent",
                num_owners=1,
                has_leather=True,
                has_nav=True,
                city="Palo Alto",
                region="Bay Area",
                source="Lexus Dealer"
            )
        ])

    if model_y_2024:
        model_y_id = model_y_2024[0]['id']
        sample_listings.extend([
            MarketPrice(
                vehicle_id=model_y_id,
                listing_date="2024-01-18",
                mileage=42000,
                asking_price=33500,
                condition="good",
                num_owners=1,
                city="Fremont",
                region="Bay Area",
                source="Private Party"
            )
        ])

    # Insert listings
    print("\nImporting sample market data...")
    for listing in sample_listings:
        price_repo.add_listing(listing)
        print(f"  - Added listing: ${listing.asking_price:,.0f} in {listing.city}")

    print(f"\n✓ Imported {len(sample_listings)} sample listings")


def main():
    """Run full data import"""
    print("=" * 80)
    print("CAR VALUATION DATABASE - DATA IMPORT")
    print("=" * 80)

    import_target_vehicles()
    import_sample_market_data()

    print("\n" + "=" * 80)
    print("DATA IMPORT COMPLETE!")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Add more market listings (manual or scrape)")
    print("  2. Run analysis and scoring")
    print("  3. Build recommendation engine")


if __name__ == "__main__":
    main()
