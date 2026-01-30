-- Car Valuation Database Schema
-- Comprehensive database for tracking vehicle values, market trends, and identifying good deals

-- Core vehicle information
CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL,
    trim TEXT,
    body_style TEXT, -- sedan, SUV, truck, etc.
    drivetrain TEXT, -- AWD, 4WD, FWD, RWD

    -- Specifications
    engine TEXT,
    transmission TEXT,
    fuel_type TEXT, -- gasoline, diesel, electric, hybrid
    horsepower INTEGER,
    torque INTEGER,

    -- Capacity
    seating_capacity INTEGER,
    cargo_capacity_cuft REAL,
    towing_capacity_lbs INTEGER,
    payload_capacity_lbs INTEGER,

    -- Efficiency
    mpg_city REAL,
    mpg_highway REAL,
    mpg_combined REAL,
    mpge REAL, -- For electric/hybrid
    battery_kwh REAL, -- For electric
    range_miles INTEGER, -- For electric

    -- Dimensions (for tall driver analysis)
    headroom_front_in REAL,
    headroom_rear_in REAL,
    legroom_front_in REAL,
    legroom_rear_in REAL,
    shoulder_room_front_in REAL,
    shoulder_room_rear_in REAL,

    -- Weight
    curb_weight_lbs INTEGER,

    -- Original pricing
    msrp REAL,
    invoice_price REAL,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(make, model, year, trim)
);

-- Market pricing data (historical and current)
CREATE TABLE IF NOT EXISTS market_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER NOT NULL,

    -- Listing details
    listing_date DATE NOT NULL,
    mileage INTEGER NOT NULL,
    asking_price REAL NOT NULL,
    sale_price REAL, -- Actual sale price if known
    sold BOOLEAN DEFAULT 0,
    sale_date DATE,

    -- Condition
    condition TEXT, -- excellent, good, fair, poor
    accident_history BOOLEAN,
    num_owners INTEGER,
    service_history_available BOOLEAN,

    -- Location
    zip_code TEXT,
    city TEXT,
    state TEXT DEFAULT 'CA',
    region TEXT, -- Bay Area, SoCal, Central Valley, etc.

    -- Features
    has_leather BOOLEAN,
    has_sunroof BOOLEAN,
    has_nav BOOLEAN,
    has_tow_package BOOLEAN,
    has_premium_audio BOOLEAN,
    color_exterior TEXT,
    color_interior TEXT,

    -- Source
    source TEXT, -- KBB, Autotrader, Craigslist, dealer, private party
    source_url TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
);

-- Reliability and problem tracking
CREATE TABLE IF NOT EXISTS reliability_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    year_start INTEGER NOT NULL,
    year_end INTEGER NOT NULL,

    -- Overall reliability
    reliability_score INTEGER, -- 1-10 scale
    predicted_reliability INTEGER, -- 1-10 scale for future

    -- Problem areas
    engine_reliability INTEGER, -- 1-10
    transmission_reliability INTEGER, -- 1-10
    electrical_reliability INTEGER, -- 1-10
    suspension_reliability INTEGER, -- 1-10
    ac_climate_reliability INTEGER, -- 1-10

    -- Source and notes
    source TEXT, -- Consumer Reports, JD Power, owner surveys
    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Common problems by vehicle
CREATE TABLE IF NOT EXISTS vehicle_problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    year_start INTEGER NOT NULL,
    year_end INTEGER NOT NULL,

    problem_category TEXT, -- Engine, Transmission, Electrical, etc.
    problem_description TEXT NOT NULL,
    severity TEXT, -- minor, moderate, major, critical
    frequency TEXT, -- rare, occasional, common, widespread
    avg_repair_cost REAL,

    -- TSB/Recall info
    has_tsb BOOLEAN DEFAULT 0,
    tsb_number TEXT,
    has_recall BOOLEAN DEFAULT 0,
    recall_number TEXT,

    source TEXT,
    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Maintenance schedules and costs
CREATE TABLE IF NOT EXISTS maintenance_costs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER NOT NULL,

    -- Service details
    service_interval_miles INTEGER,
    service_type TEXT, -- oil change, tire rotation, major service, etc.
    avg_cost REAL,

    -- Location-based costs
    region TEXT DEFAULT 'Bay Area',
    dealer_cost REAL,
    independent_shop_cost REAL,
    diy_parts_cost REAL,

    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
);

-- Depreciation tracking
CREATE TABLE IF NOT EXISTS depreciation_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL,

    -- Depreciation percentages
    year_1_depreciation REAL, -- Percentage
    year_2_depreciation REAL,
    year_3_depreciation REAL,
    year_5_depreciation REAL,

    -- Residual value estimates
    residual_value_3yr_36k REAL, -- Percentage of MSRP
    residual_value_5yr_60k REAL,

    -- Market demand factors
    demand_score INTEGER, -- 1-10
    supply_score INTEGER, -- 1-10 (low = rare/hard to find)

    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Driver fit and comfort ratings
CREATE TABLE IF NOT EXISTS driver_fit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER NOT NULL,

    -- Height suitability (inches)
    recommended_height_min INTEGER,
    recommended_height_max INTEGER,

    -- Comfort scores (1-10)
    seat_comfort_score INTEGER,
    seat_adjustability_score INTEGER, -- range of adjustment
    lumbar_support_score INTEGER,
    seat_material_quality INTEGER,

    -- Ergonomics
    steering_wheel_adjustability INTEGER, -- tilt and telescope
    pedal_position_score INTEGER,
    visibility_score INTEGER,

    -- Specific for tall drivers
    tall_driver_suitable BOOLEAN, -- 6'3"+
    tall_driver_notes TEXT,

    -- Testing notes
    tested_by TEXT,
    tester_height INTEGER,
    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
);

-- Regional market analysis
CREATE TABLE IF NOT EXISTS regional_markets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    region TEXT NOT NULL,
    state TEXT DEFAULT 'CA',

    -- Market characteristics
    avg_vehicle_price REAL,
    inventory_level TEXT, -- low, medium, high
    buyer_competition TEXT, -- low, medium, high
    seller_advantage BOOLEAN,

    -- Price modifiers
    price_premium_percentage REAL, -- vs national average
    luxury_vehicle_premium REAL,
    truck_suv_premium REAL,

    -- Best for
    good_for_buying BOOLEAN,
    good_for_selling BOOLEAN,

    notes TEXT,
    date_updated DATE,

    UNIQUE(region, state)
);

-- User watchlist and saved searches
CREATE TABLE IF NOT EXISTS user_watchlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Search criteria
    make TEXT,
    model TEXT,
    year_min INTEGER,
    year_max INTEGER,
    price_max REAL,
    mileage_max INTEGER,

    -- Must-have features
    require_4wd BOOLEAN DEFAULT 0,
    require_leather BOOLEAN DEFAULT 0,
    require_tow_package BOOLEAN DEFAULT 0,

    -- Regions to search
    regions TEXT, -- JSON array

    -- Alerts
    notify_on_new_listing BOOLEAN DEFAULT 1,
    notify_on_price_drop BOOLEAN DEFAULT 1,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Deal scores and opportunities
CREATE TABLE IF NOT EXISTS deal_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_price_id INTEGER NOT NULL,

    -- Scoring
    deal_score INTEGER, -- 1-100, higher = better deal

    -- Price analysis
    fair_market_value REAL,
    price_vs_market REAL, -- Percentage difference

    -- Value factors
    reliability_adjusted_value REAL,
    maintenance_cost_factor REAL,
    resale_potential_score INTEGER,

    -- Total cost of ownership projection
    tco_1year REAL,
    tco_3year REAL,
    tco_5year REAL,

    -- Recommendation
    buy_recommendation TEXT, -- strong buy, buy, hold, avoid
    negotiation_target_price REAL,

    notes TEXT,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (market_price_id) REFERENCES market_prices(id)
);

-- Feature packages and options
CREATE TABLE IF NOT EXISTS feature_packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL,

    package_name TEXT NOT NULL,
    package_code TEXT,
    includes TEXT, -- JSON array of features
    msrp_add REAL, -- Additional cost
    resale_value_add REAL, -- Additional resale value

    desirability_score INTEGER, -- 1-10

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Negotiation strategies and tips
CREATE TABLE IF NOT EXISTS negotiation_strategies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    vehicle_category TEXT, -- luxury, truck, suv, electric, etc.
    market_condition TEXT, -- seller's market, buyer's market, balanced

    strategy_name TEXT NOT NULL,
    strategy_description TEXT,

    -- Tactics
    initial_offer_percentage REAL, -- % below asking
    walkaway_percentage REAL, -- % below asking to walk away

    timing_tips TEXT,
    leverage_points TEXT,

    success_rate REAL,
    avg_savings_percentage REAL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_vehicles_make_model_year ON vehicles(make, model, year);
CREATE INDEX IF NOT EXISTS idx_market_prices_vehicle ON market_prices(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_market_prices_region ON market_prices(region);
CREATE INDEX IF NOT EXISTS idx_market_prices_date ON market_prices(listing_date);
CREATE INDEX IF NOT EXISTS idx_reliability_make_model ON reliability_data(make, model);
CREATE INDEX IF NOT EXISTS idx_problems_make_model ON vehicle_problems(make, model);
CREATE INDEX IF NOT EXISTS idx_deal_scores_score ON deal_scores(deal_score DESC);
