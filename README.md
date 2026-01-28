# Vehicle Optimization System

A comprehensive analysis tool for optimizing vehicle ownership decisions based on depreciation, total cost of ownership, and functionality requirements.

## Overview

This system analyzes multiple vehicle ownership scenarios to help you make data-driven decisions about:
- Whether to keep your current vehicle or switch
- Which replacement vehicle best fits your needs
- Timing of vehicle transactions to maximize value
- Trade-offs between single and dual-vehicle ownership
- Impact of adding trailers or equipment

## Your Specific Situation

- **Current Vehicle**: 2024 Tesla Model Y AWD Long Range
- **Purchase Price**: $35,000 (used, with FSD)
- **Current Mileage**: 42,000 miles
- **Annual Mileage**: ~20,000 miles/year
- **Pending Credits**: $6,000 (available June 2026)
- **Location**: Bay Area, California

## Key Features

### 1. Depreciation Modeling
- Multi-factor depreciation calculation
- Considers age, mileage, brand reliability, and market demand
- Projects future values with monthly granularity
- Accounts for high-mileage depreciation penalties

### 2. Total Cost of Ownership
- Acquisition costs (purchase, tax, registration, fees)
- Operating costs (fuel, insurance, maintenance, storage)
- Future vehicle values and resale potential
- Credits and incentives timing

### 3. Functionality Scoring
- Weighted scoring based on your priorities:
  - Cargo capacity (20%)
  - Legroom/comfort (30% combined) - critical for hip problems
  - Outdoor capability (25%) - towing, AWD, roof racks
  - Range (15%) - long-distance and Baja trips
  - Cost efficiency (10%)

### 4. Scenario Comparison
- Analyzes 11+ different scenarios
- Ranks by overall recommendation score (60% functionality, 40% financial)
- Provides detailed breakdowns for top scenarios

## Files

- `vehicle_optimizer.py` - Core engine with depreciation, cost, and scoring models
- `vehicle_database.py` - Real vehicle specifications and Bay Area pricing
- `scenario_builder.py` - Builds specific scenarios to analyze
- `analysis.py` - Main analysis script with reporting
- `vehicle_analysis_results.json` - Detailed output data (generated)

## Scenarios Analyzed

1. **Keep Tesla 6mo (Get Credits)** - Hold until credits vest
2. **Sell Now → Tacoma** - Trade for new Tacoma
3. **Sell Now → Lexus GX** - Trade for Lexus GX 550
4. **Sell Now → Lexus LX** - Trade for Lexus LX 600
5. **Sell Now → Escalade** - Trade for Cadillac Escalade
6. **Sell Now → F-150** - Trade for Ford F-150
7. **Sell Now → 4Runner** - Trade for Toyota 4Runner
8. **Sell Now → Tacoma + A-Liner Trailer** - Truck + camping setup
9. **Keep Tesla + Used Tacoma (Dual)** - Two-vehicle setup
10. **Wait 6mo (Credits) → Lexus GX** - Optimal timing strategy
11. **Sell Now → Lexus GX + Taxa Mantis** - Premium adventure setup

## Usage

Run the complete analysis:
```bash
python analysis.py
```

This will:
1. Analyze all scenarios
2. Calculate financial positions
3. Score functionality
4. Generate rankings
5. Output detailed report
6. Export JSON data

## Key Assumptions

- **Bay Area sales tax**: 9.25%
- **Gas price**: $4.50/gallon
- **Electricity rate**: $0.35/kWh (PG&E peak)
- **Annual mileage**: 20,000 miles
- **Analysis period**: 36 months
- **Storage cost**: $250/month (if needed)

## Methodology

### Recommendation Score Calculation
```
Overall Score = (Financial Score × 0.4) + (Functionality Score × 0.6)
```

The heavier weight on functionality reflects your prioritization of practical needs over pure financial optimization.

### Depreciation Factors
- Vehicle age and mileage
- Brand reliability scores (Toyota/Lexus: 9.5/10)
- Market demand patterns
- High-mileage penalties for EVs
- Warranty thresholds

### Net Position Calculation
```
Net Position = Future Vehicle Value(s) + Credits - Total Costs
Total Costs = Acquisition + Operating Costs
```

## Results Interpretation

- **Positive Net Position**: You end up ahead financially
- **Negative Net Position**: Net cost to own over period
- **Recommendation Score**: Higher is better (max 10)
- **Functionality Score**: How well it meets your needs (max 10)

## Customization

To modify scenarios or add new vehicles:
1. Edit `vehicle_database.py` to add vehicles
2. Edit `scenario_builder.py` to create new scenarios
3. Adjust priorities in `get_user_priorities()`

## Notes

- Trade-in values are estimates; get actual quotes
- Insurance costs are Bay Area averages; get real quotes
- Gas prices assumed constant (adjust for volatility)
- Maintenance costs based on historical data
- Value retention varies by market conditions
