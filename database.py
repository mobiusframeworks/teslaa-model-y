"""
Database Manager for Car Valuation System
Handles all SQL database operations
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager
from dataclasses import dataclass, asdict


class DatabaseManager:
    """Manages SQLite database connections and operations"""

    def __init__(self, db_path: str = "car_valuation.db"):
        self.db_path = db_path
        self.initialize_database()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize_database(self):
        """Create database schema if it doesn't exist"""
        schema_path = Path(__file__).parent / "database_schema.sql"

        with self.get_connection() as conn:
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
                conn.executescript(schema_sql)

        print(f"Database initialized: {self.db_path}")

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute a SELECT query and return results as list of dicts"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def execute_write(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return last row id"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.lastrowid


@dataclass
class Vehicle:
    """Core vehicle data model"""
    make: str
    model: str
    year: int
    trim: str = ""
    body_style: str = ""
    drivetrain: str = ""

    # Specs
    engine: str = ""
    transmission: str = ""
    fuel_type: str = "gasoline"
    horsepower: int = 0
    torque: int = 0

    # Capacity
    seating_capacity: int = 5
    cargo_capacity_cuft: float = 0
    towing_capacity_lbs: int = 0
    payload_capacity_lbs: int = 0

    # Efficiency
    mpg_city: float = 0
    mpg_highway: float = 0
    mpg_combined: float = 0
    mpge: float = 0
    battery_kwh: float = 0
    range_miles: int = 0

    # Dimensions
    headroom_front_in: float = 0
    headroom_rear_in: float = 0
    legroom_front_in: float = 0
    legroom_rear_in: float = 0
    shoulder_room_front_in: float = 0
    shoulder_room_rear_in: float = 0

    # Weight
    curb_weight_lbs: int = 0

    # Pricing
    msrp: float = 0
    invoice_price: float = 0

    # Internal
    id: Optional[int] = None

    def to_dict(self):
        """Convert to dictionary, excluding None values"""
        return {k: v for k, v in asdict(self).items() if v is not None and k != 'id'}


@dataclass
class MarketPrice:
    """Market listing data"""
    vehicle_id: int
    listing_date: str
    mileage: int
    asking_price: float

    # Optional fields
    sale_price: Optional[float] = None
    sold: bool = False
    sale_date: Optional[str] = None

    condition: str = "good"
    accident_history: bool = False
    num_owners: int = 1
    service_history_available: bool = False

    # Location
    zip_code: str = ""
    city: str = ""
    state: str = "CA"
    region: str = ""

    # Features
    has_leather: bool = False
    has_sunroof: bool = False
    has_nav: bool = False
    has_tow_package: bool = False
    has_premium_audio: bool = False
    color_exterior: str = ""
    color_interior: str = ""

    # Source
    source: str = "manual"
    source_url: str = ""

    id: Optional[int] = None


@dataclass
class VehicleProblem:
    """Known problems for a vehicle"""
    make: str
    model: str
    year_start: int
    year_end: int
    problem_category: str
    problem_description: str

    severity: str = "moderate"  # minor, moderate, major, critical
    frequency: str = "occasional"  # rare, occasional, common, widespread
    avg_repair_cost: float = 0

    has_tsb: bool = False
    tsb_number: str = ""
    has_recall: bool = False
    recall_number: str = ""

    source: str = ""
    notes: str = ""

    id: Optional[int] = None


@dataclass
class DriverFit:
    """Driver comfort and fit data"""
    vehicle_id: int

    recommended_height_min: int = 60  # 5'0"
    recommended_height_max: int = 76  # 6'4"

    # Comfort scores 1-10
    seat_comfort_score: int = 5
    seat_adjustability_score: int = 5
    lumbar_support_score: int = 5
    seat_material_quality: int = 5

    steering_wheel_adjustability: int = 5
    pedal_position_score: int = 5
    visibility_score: int = 5

    tall_driver_suitable: bool = True
    tall_driver_notes: str = ""

    tested_by: str = ""
    tester_height: int = 0
    notes: str = ""

    id: Optional[int] = None


class VehicleRepository:
    """Repository for vehicle CRUD operations"""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def create_vehicle(self, vehicle: Vehicle) -> int:
        """Insert a new vehicle and return its ID"""
        data = vehicle.to_dict()
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO vehicles ({columns}) VALUES ({placeholders})"

        return self.db.execute_write(query, tuple(data.values()))

    def get_vehicle(self, vehicle_id: int) -> Optional[Dict]:
        """Get vehicle by ID"""
        query = "SELECT * FROM vehicles WHERE id = ?"
        results = self.db.execute_query(query, (vehicle_id,))
        return results[0] if results else None

    def find_vehicles(self, make: str = None, model: str = None,
                     year_min: int = None, year_max: int = None) -> List[Dict]:
        """Find vehicles matching criteria"""
        conditions = []
        params = []

        if make:
            conditions.append("make = ?")
            params.append(make)
        if model:
            conditions.append("model = ?")
            params.append(model)
        if year_min:
            conditions.append("year >= ?")
            params.append(year_min)
        if year_max:
            conditions.append("year <= ?")
            params.append(year_max)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = f"SELECT * FROM vehicles WHERE {where_clause} ORDER BY year DESC"

        return self.db.execute_query(query, tuple(params))

    def get_or_create_vehicle(self, vehicle: Vehicle) -> int:
        """Get existing vehicle ID or create new one"""
        existing = self.db.execute_query(
            "SELECT id FROM vehicles WHERE make = ? AND model = ? AND year = ? AND trim = ?",
            (vehicle.make, vehicle.model, vehicle.year, vehicle.trim)
        )

        if existing:
            return existing[0]['id']
        else:
            return self.create_vehicle(vehicle)


class MarketPriceRepository:
    """Repository for market pricing data"""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def add_listing(self, listing: MarketPrice) -> int:
        """Add a market listing"""
        data = asdict(listing)
        data.pop('id', None)

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO market_prices ({columns}) VALUES ({placeholders})"

        return self.db.execute_write(query, tuple(data.values()))

    def get_listings(self, vehicle_id: int = None, region: str = None,
                    min_date: str = None, sold_only: bool = False) -> List[Dict]:
        """Get market listings with filters"""
        conditions = []
        params = []

        if vehicle_id:
            conditions.append("vehicle_id = ?")
            params.append(vehicle_id)
        if region:
            conditions.append("region = ?")
            params.append(region)
        if min_date:
            conditions.append("listing_date >= ?")
            params.append(min_date)
        if sold_only:
            conditions.append("sold = 1")

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = f"""
            SELECT mp.*, v.make, v.model, v.year, v.trim
            FROM market_prices mp
            JOIN vehicles v ON mp.vehicle_id = v.id
            WHERE {where_clause}
            ORDER BY listing_date DESC
        """

        return self.db.execute_query(query, tuple(params))

    def get_market_statistics(self, make: str, model: str, year: int,
                              region: str = None) -> Dict:
        """Get market statistics for a vehicle"""
        conditions = ["v.make = ?", "v.model = ?", "v.year = ?"]
        params = [make, model, year]

        if region:
            conditions.append("mp.region = ?")
            params.append(region)

        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT
                COUNT(*) as listing_count,
                AVG(mp.asking_price) as avg_price,
                MIN(mp.asking_price) as min_price,
                MAX(mp.asking_price) as max_price,
                AVG(mp.mileage) as avg_mileage,
                COUNT(CASE WHEN mp.sold = 1 THEN 1 END) as sold_count,
                AVG(CASE WHEN mp.sold = 1 THEN mp.sale_price END) as avg_sale_price
            FROM market_prices mp
            JOIN vehicles v ON mp.vehicle_id = v.id
            WHERE {where_clause}
        """

        results = self.db.execute_query(query, tuple(params))
        return results[0] if results else {}


class ProblemRepository:
    """Repository for vehicle problems and reliability"""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def add_problem(self, problem: VehicleProblem) -> int:
        """Add a known problem"""
        data = asdict(problem)
        data.pop('id', None)

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO vehicle_problems ({columns}) VALUES ({placeholders})"

        return self.db.execute_write(query, tuple(data.values()))

    def get_problems(self, make: str, model: str, year: int = None) -> List[Dict]:
        """Get known problems for a vehicle"""
        if year:
            query = """
                SELECT * FROM vehicle_problems
                WHERE make = ? AND model = ? AND year_start <= ? AND year_end >= ?
                ORDER BY severity DESC, frequency DESC
            """
            params = (make, model, year, year)
        else:
            query = """
                SELECT * FROM vehicle_problems
                WHERE make = ? AND model = ?
                ORDER BY year_start DESC, severity DESC
            """
            params = (make, model)

        return self.db.execute_query(query, params)

    def add_reliability_data(self, make: str, model: str, year_start: int,
                            year_end: int, reliability_score: int, **kwargs) -> int:
        """Add reliability data"""
        query = """
            INSERT INTO reliability_data
            (make, model, year_start, year_end, reliability_score)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.db.execute_write(query, (make, model, year_start, year_end, reliability_score))


class DriverFitRepository:
    """Repository for driver fit and comfort data"""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def add_fit_data(self, fit_data: DriverFit) -> int:
        """Add driver fit data for a vehicle"""
        data = asdict(fit_data)
        data.pop('id', None)

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO driver_fit ({columns}) VALUES ({placeholders})"

        return self.db.execute_write(query, tuple(data.values()))

    def get_fit_data(self, vehicle_id: int) -> Optional[Dict]:
        """Get driver fit data for a vehicle"""
        query = "SELECT * FROM driver_fit WHERE vehicle_id = ?"
        results = self.db.execute_query(query, (vehicle_id,))
        return results[0] if results else None

    def find_suitable_vehicles(self, driver_height: int, min_comfort: int = 7) -> List[Dict]:
        """Find vehicles suitable for a driver height"""
        query = """
            SELECT v.*, df.seat_comfort_score, df.seat_adjustability_score,
                   df.tall_driver_suitable, df.tall_driver_notes
            FROM vehicles v
            JOIN driver_fit df ON v.id = df.vehicle_id
            WHERE df.recommended_height_min <= ?
              AND df.recommended_height_max >= ?
              AND df.seat_comfort_score >= ?
            ORDER BY df.seat_comfort_score DESC, df.seat_adjustability_score DESC
        """
        return self.db.execute_query(query, (driver_height, driver_height, min_comfort))


def main():
    """Initialize database and run basic tests"""
    print("Initializing Car Valuation Database...")

    db = DatabaseManager()

    print("\nDatabase tables created successfully!")
    print(f"Database file: {db.db_path}")

    # Test: Create a sample vehicle
    vehicle_repo = VehicleRepository(db)

    test_vehicle = Vehicle(
        make="Toyota",
        model="Tacoma",
        year=2024,
        trim="TRD Off-Road",
        body_style="Truck",
        drivetrain="4WD",
        fuel_type="gasoline",
        seating_capacity=5,
        cargo_capacity_cuft=61,
        towing_capacity_lbs=6500,
        mpg_city=19,
        mpg_highway=24,
        legroom_front_in=42.9,
        legroom_rear_in=34.6,
        msrp=47995
    )

    vehicle_id = vehicle_repo.create_vehicle(test_vehicle)
    print(f"\nTest vehicle created with ID: {vehicle_id}")

    # Verify
    retrieved = vehicle_repo.get_vehicle(vehicle_id)
    print(f"Retrieved: {retrieved['year']} {retrieved['make']} {retrieved['model']} {retrieved['trim']}")

    print("\nDatabase initialization complete!")


if __name__ == "__main__":
    main()
