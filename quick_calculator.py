"""
Quick Calculator - Interactive tool for what-if scenarios
Run this to quickly calculate different scenarios
"""

from vehicle_optimizer import DepreciationModel
from scenario_builder import estimate_tesla_trade_in


def calculate_wait_vs_sell_now(months_to_wait: int = 6, credits: float = 6000):
    """
    Calculate whether waiting for credits is worth it vs selling now
    """
    print(f"\n{'='*70}")
    print(f"WAIT {months_to_wait} MONTHS vs SELL NOW ANALYSIS")
    print(f"{'='*70}\n")

    # Current value
    current_value = estimate_tesla_trade_in(0)
    future_value = estimate_tesla_trade_in(months_to_wait)

    # Depreciation
    total_depreciation = current_value - future_value
    monthly_depreciation = total_depreciation / months_to_wait

    # Net calculation
    net_benefit = credits - total_depreciation

    print(f"Current Tesla Trade-in Value:     ${current_value:,.0f}")
    print(f"Value after {months_to_wait} months:          ${future_value:,.0f}")
    print(f"Total Depreciation:               ${total_depreciation:,.0f}")
    print(f"  (${monthly_depreciation:,.0f}/month average)")
    print(f"\nCredits after {months_to_wait} months:        ${credits:,.0f}")
    print(f"\n{'─'*70}")
    print(f"NET BENEFIT OF WAITING:           ${net_benefit:,.0f}")
    print(f"{'─'*70}\n")

    if net_benefit > 1000:
        print(f"✅ RECOMMENDATION: Wait {months_to_wait} months to collect credits")
        print(f"   You gain ${net_benefit:,.0f} by waiting")
    elif net_benefit > 0:
        print(f"⚠️  MARGINAL: Small benefit (${net_benefit:,.0f}) to waiting")
        print(f"   Consider personal urgency to switch")
    else:
        print(f"❌ RECOMMENDATION: Sell now")
        print(f"   You lose ${abs(net_benefit):,.0f} by waiting")

    return {
        'current_value': current_value,
        'future_value': future_value,
        'depreciation': total_depreciation,
        'credits': credits,
        'net_benefit': net_benefit
    }


def calculate_operating_cost_comparison(vehicle1_mpg: float, vehicle2_mpg: float,
                                       annual_miles: int = 20000, gas_price: float = 4.50):
    """
    Compare operating costs between two vehicles
    vehicle1_mpg: Use 0 for Tesla (electric)
    """
    print(f"\n{'='*70}")
    print(f"OPERATING COST COMPARISON")
    print(f"{'='*70}\n")
    print(f"Annual Mileage: {annual_miles:,} miles")
    print(f"Gas Price: ${gas_price}/gallon")
    print(f"\n{'─'*70}\n")

    # Vehicle 1 (assume Tesla if mpg = 0)
    if vehicle1_mpg == 0:
        v1_name = "Tesla Model Y (Electric)"
        v1_cost_per_mile = 0.04  # $0.04/mile for electricity
        v1_annual_fuel = v1_cost_per_mile * annual_miles
    else:
        v1_name = f"Vehicle 1 ({vehicle1_mpg} MPG)"
        v1_cost_per_mile = gas_price / vehicle1_mpg
        v1_annual_fuel = (annual_miles / vehicle1_mpg) * gas_price

    # Vehicle 2
    v2_name = f"Vehicle 2 ({vehicle2_mpg} MPG)"
    v2_cost_per_mile = gas_price / vehicle2_mpg
    v2_annual_fuel = (annual_miles / vehicle2_mpg) * gas_price

    # Comparison
    difference_annual = v2_annual_fuel - v1_annual_fuel
    difference_monthly = difference_annual / 12
    difference_per_mile = v2_cost_per_mile - v1_cost_per_mile

    print(f"{v1_name}")
    print(f"  Cost per mile:    ${v1_cost_per_mile:.3f}")
    print(f"  Annual fuel:      ${v1_annual_fuel:,.0f}")
    print(f"  Monthly fuel:     ${v1_annual_fuel/12:,.0f}")

    print(f"\n{v2_name}")
    print(f"  Cost per mile:    ${v2_cost_per_mile:.3f}")
    print(f"  Annual fuel:      ${v2_annual_fuel:,.0f}")
    print(f"  Monthly fuel:     ${v2_annual_fuel/12:,.0f}")

    print(f"\n{'─'*70}")
    print(f"DIFFERENCE:")
    print(f"  Per mile:         ${difference_per_mile:.3f} more")
    print(f"  Per month:        ${difference_monthly:,.0f} more")
    print(f"  Per year:         ${difference_annual:,.0f} more")
    print(f"  Over 3 years:     ${difference_annual * 3:,.0f} more")
    print(f"{'─'*70}\n")

    return {
        'v1_annual': v1_annual_fuel,
        'v2_annual': v2_annual_fuel,
        'difference_annual': difference_annual,
        'difference_monthly': difference_monthly
    }


def calculate_total_switch_cost(current_value: float, new_vehicle_price: float,
                               sales_tax_rate: float = 0.0925):
    """
    Calculate total upfront cost to switch vehicles
    """
    print(f"\n{'='*70}")
    print(f"VEHICLE SWITCH COST CALCULATOR")
    print(f"{'='*70}\n")

    net_price = new_vehicle_price - current_value
    sales_tax = net_price * sales_tax_rate
    registration = 500  # Bay Area average
    transfer_fee = 85
    doc_fee = 200  # Average dealer doc fee

    total = net_price + sales_tax + registration + transfer_fee + doc_fee

    print(f"New Vehicle Price:                ${new_vehicle_price:,.0f}")
    print(f"Your Trade-in Value:              ${current_value:,.0f}")
    print(f"{'─'*70}")
    print(f"Net Price:                        ${net_price:,.0f}")
    print(f"\nAdditional Costs:")
    print(f"  Sales Tax ({sales_tax_rate*100:.2f}%):         ${sales_tax:,.0f}")
    print(f"  Registration:                   ${registration:,.0f}")
    print(f"  Transfer Fee:                   ${transfer_fee:,.0f}")
    print(f"  Doc Fee:                        ${doc_fee:,.0f}")
    print(f"{'─'*70}")
    print(f"TOTAL CASH NEEDED:                ${total:,.0f}")
    print(f"{'─'*70}\n")

    return {
        'net_price': net_price,
        'sales_tax': sales_tax,
        'total': total
    }


def calculate_breakeven_years(purchase_premium: float, annual_savings: float):
    """
    Calculate how many years to break even on a more expensive vehicle with lower operating costs
    """
    if annual_savings <= 0:
        print("Annual savings must be positive")
        return None

    breakeven = purchase_premium / annual_savings

    print(f"\n{'='*70}")
    print(f"BREAKEVEN ANALYSIS")
    print(f"{'='*70}\n")
    print(f"Additional Purchase Cost:         ${purchase_premium:,.0f}")
    print(f"Annual Operating Savings:         ${annual_savings:,.0f}")
    print(f"\n{'─'*70}")
    print(f"BREAKEVEN POINT:                  {breakeven:.1f} years")
    print(f"{'─'*70}\n")

    if breakeven < 3:
        print(f"✅ Good ROI - Break even in under 3 years")
    elif breakeven < 5:
        print(f"⚠️  Marginal ROI - Break even in {breakeven:.1f} years")
    else:
        print(f"❌ Poor ROI - Takes {breakeven:.1f} years to break even")

    return breakeven


def main_menu():
    """Interactive menu for quick calculations"""
    print(f"\n{'='*70}")
    print(f"VEHICLE OPTIMIZATION - QUICK CALCULATOR")
    print(f"{'='*70}\n")

    print("Select a calculation:\n")
    print("1. Wait for Credits vs. Sell Now")
    print("2. Operating Cost Comparison (Tesla vs. Gas vehicle)")
    print("3. Total Cost to Switch Vehicles")
    print("4. Breakeven Analysis")
    print("5. Run All Calculations")
    print("0. Exit\n")

    choice = input("Enter choice (0-5): ").strip()

    if choice == "1":
        months = int(input("Months to wait (default 6): ") or "6")
        credits = float(input("Credits to receive (default 6000): ") or "6000")
        calculate_wait_vs_sell_now(months, credits)

    elif choice == "2":
        print("\nTesla (electric) = 0 MPG")
        v1_mpg = float(input("Vehicle 1 MPG (0 for Tesla): ") or "0")
        v2_mpg = float(input("Vehicle 2 MPG: ") or "18")
        miles = int(input("Annual mileage (default 20000): ") or "20000")
        gas = float(input("Gas price per gallon (default 4.50): ") or "4.50")
        calculate_operating_cost_comparison(v1_mpg, v2_mpg, miles, gas)

    elif choice == "3":
        current = float(input("Current vehicle trade-in value: ") or "30450")
        new = float(input("New vehicle price: ") or "52000")
        calculate_total_switch_cost(current, new)

    elif choice == "4":
        premium = float(input("Additional purchase cost: "))
        savings = float(input("Annual operating cost savings: "))
        calculate_breakeven_years(premium, savings)

    elif choice == "5":
        # Run all default calculations
        print("\n\n" + "▼"*70)
        calculate_wait_vs_sell_now()
        print("\n\n" + "▼"*70)
        calculate_operating_cost_comparison(0, 18)  # Tesla vs 18 MPG
        print("\n\n" + "▼"*70)
        calculate_total_switch_cost(30450, 52000)  # Tesla → 4Runner
        print("\n\n" + "▼"*70)

    elif choice == "0":
        print("Exiting...")
        return False

    return True


if __name__ == "__main__":
    # Run default analysis
    print("\n" + "="*70)
    print("RUNNING DEFAULT SCENARIOS FOR YOUR SITUATION")
    print("="*70)

    # Scenario 1: Wait 6 months
    calculate_wait_vs_sell_now(6, 6000)

    # Scenario 2: Tesla vs 4Runner operating costs
    print("\n\n" + "▼"*70 + "\n")
    print("TESLA vs TOYOTA 4RUNNER (18 MPG Combined)")
    calculate_operating_cost_comparison(0, 18, 20000, 4.50)

    # Scenario 3: Cost to switch to 4Runner
    print("\n\n" + "▼"*70 + "\n")
    print("SWITCHING TO 2024 TOYOTA 4RUNNER")
    calculate_total_switch_cost(30450, 52000)

    # Scenario 4: Tesla vs Tacoma
    print("\n\n" + "▼"*70 + "\n")
    print("TESLA vs TOYOTA TACOMA (21 MPG Combined)")
    calculate_operating_cost_comparison(0, 21, 20000, 4.50)

    # Scenario 5: Cost to switch to Tacoma
    print("\n\n" + "▼"*70 + "\n")
    print("SWITCHING TO 2025 TOYOTA TACOMA")
    calculate_total_switch_cost(30450, 48000)

    print("\n\n" + "="*70)
    print("QUICK ANALYSIS COMPLETE")
    print("="*70 + "\n")
    print("For full detailed analysis, run: python3 analysis.py")
    print("For interactive mode, uncomment the main_menu() section")
