"""
Main Analysis Script
Runs comprehensive vehicle optimization analysis and generates report
"""

import json
from datetime import datetime
from vehicle_optimizer import ScenarioAnalyzer, DepreciationModel
from scenario_builder import build_all_scenarios, get_user_priorities, estimate_tesla_trade_in


def print_header(title: str, char: str = "="):
    """Print formatted section header"""
    print(f"\n{char * 80}")
    print(f"{title.center(80)}")
    print(f"{char * 80}\n")


def print_section(title: str):
    """Print formatted subsection"""
    print(f"\n{title}")
    print("-" * len(title))


def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:,.0f}"


def format_score(score: float, max_score: float = 10) -> str:
    """Format score with visual bar"""
    filled = int((score / max_score) * 20)
    bar = "█" * filled + "░" * (20 - filled)
    return f"{score:.1f}/10 [{bar}]"


def print_comparison_table(comparison_data: list):
    """Print formatted comparison table"""
    print_section("Scenario Comparison Summary")

    # Header
    print(f"{'Rank':<6}{'Scenario':<35}{'Score':<12}{'Func':<12}{'Net Position':<16}{'Monthly Cost':<15}")
    print("-" * 100)

    # Data rows
    for i, scenario in enumerate(comparison_data, 1):
        rank_symbol = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f" {i}."

        print(
            f"{rank_symbol:<6}"
            f"{scenario['scenario']:<35}"
            f"{scenario['recommendation_score']:<12.1f}"
            f"{scenario['functionality_score']:<12.1f}"
            f"{format_currency(scenario['net_position']):<16}"
            f"{format_currency(scenario['monthly_cost']):<15}"
        )


def print_detailed_scenario(analysis: dict):
    """Print detailed analysis for a single scenario"""
    print_header(f"DETAILED ANALYSIS: {analysis['scenario_name']}", "=")

    # Overall scores
    print_section("Overall Assessment")
    print(f"Recommendation Score: {format_score(analysis['recommendation_score'])}")
    print(f"Functionality Score:  {format_score(analysis['functionality_score'])}")

    # Financial summary
    fin = analysis['financial_summary']
    print_section("Financial Summary (36-month period)")

    print(f"\nInitial Costs:")
    acq = fin['acquisition_costs']
    print(f"  Purchase Price:     {format_currency(acq['purchase_price'])}")
    print(f"  Trade-in Credit:    {format_currency(acq['trade_in_credit'])}")
    print(f"  Sales Tax:          {format_currency(acq['sales_tax'])}")
    print(f"  Registration/Fees:  {format_currency(acq['registration'] + acq['transfer_fees'])}")
    if acq.get('trailer', 0) > 0:
        print(f"  Trailer:            {format_currency(acq['trailer'])}")
    print(f"  Total Acquisition:  {format_currency(acq['total_acquisition'])}")

    print(f"\nOperating Costs:")
    ops = fin['operating_costs']
    for key, value in ops.items():
        if key != 'total_operating' and value > 0:
            label = key.replace('_', ' ').title()
            print(f"  {label:<20}{format_currency(value)}")
    print(f"  Total Operating:    {format_currency(ops['total_operating'])}")

    print(f"\nEnd-of-Period Position:")
    print(f"  Vehicle Value(s):   {format_currency(fin['total_future_value'])}")
    if fin['credits'] > 0:
        print(f"  Credits Received:   {format_currency(fin['credits'])}")
    print(f"  Total Costs:        {format_currency(fin['total_costs'])}")
    print(f"\n  NET POSITION:       {format_currency(fin['net_position'])}")
    print(f"  Equivalent Monthly: {format_currency(fin['equivalent_monthly_cost'])}")

    # Functionality breakdown
    print_section("Functionality Breakdown")
    for vehicle_score in analysis['functionality_details']:
        vehicle_name = next((v for k, v in vehicle_score.items() if 'vehicle_' in k), "Vehicle")
        print(f"\n{vehicle_name}:")
        breakdown = vehicle_score['breakdown']
        for feature, score in breakdown.items():
            feature_label = feature.replace('_', ' ').title()
            print(f"  {feature_label:<20}{format_score(score)}")

    # Depreciation analysis
    print_section("Depreciation Analysis")
    for dep in analysis['depreciation_analysis']:
        print(f"\n{dep['vehicle']}:")
        print(f"  Current Value:      {format_currency(dep['current_value'])}")
        print(f"  Future Value:       {format_currency(dep['future_value'])}")
        print(f"  Total Depreciation: {format_currency(dep['total_depreciation'])}")
        print(f"  Retention Rate:     {(dep['future_value']/dep['current_value']*100):.1f}%")


def generate_tesla_timeline():
    """Generate Tesla value timeline if held"""
    print_header("TESLA MODEL Y VALUE PROJECTION", "=")
    print("If you keep driving the Tesla at current pace (20k miles/year):\n")

    print(f"{'Month':<8}{'Miles':<10}{'Trade-in Value':<18}{'Monthly Drop':<15}{'Credits':<15}")
    print("-" * 80)

    prev_value = None
    for month in [0, 3, 6, 9, 12, 18, 24, 36]:
        miles = 42000 + (month * 1667)
        trade_in = estimate_tesla_trade_in(month)
        monthly_drop = "" if prev_value is None else format_currency((prev_value - trade_in) / max(month - prev_month, 1))
        credits = "$6,000" if month >= 6 else "-"

        print(f"{month:<8}{miles:<10,}{format_currency(trade_in):<18}{monthly_drop:<15}{credits:<15}")

        prev_value = trade_in
        prev_month = month

    print("\nKey observations:")
    print("  • You'll receive $6,000 in credits at month 6 (June)")
    print("  • Tesla is depreciating ~$400-600/month at high mileage")
    print("  • Approaching 50k miles reduces warranty protection")
    print("  • High mileage EVs depreciate faster than ICE vehicles")


def main():
    """Run complete analysis"""
    print_header("VEHICLE OPTIMIZATION ANALYSIS", "=")
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("For: Bay Area Outdoor Enthusiast | Hip Problems | 20k miles/year")
    print("\nCurrent Vehicle: 2024 Tesla Model Y AWD LR | 42,000 miles | $35k purchase")

    # Show user priorities
    print_section("Your Priorities (Weighted)")
    priorities = get_user_priorities()
    for feature, weight in sorted(priorities.items(), key=lambda x: x[1], reverse=True):
        feature_label = feature.replace('_', ' ').title()
        print(f"  {feature_label:<20}{weight*100:>5.0f}%")

    # Tesla timeline
    generate_tesla_timeline()

    # Build and analyze all scenarios
    print_header("ANALYZING ALL SCENARIOS...", "=")
    scenarios = build_all_scenarios()
    analyzer = ScenarioAnalyzer(get_user_priorities())

    print(f"Running analysis on {len(scenarios)} scenarios...")
    comparison_result = analyzer.compare_scenarios(scenarios)

    # Print comparison table
    print_header("RESULTS", "=")
    print_comparison_table(comparison_result['comparison_summary'])

    # Print top 3 detailed analyses
    print_header("TOP 3 RECOMMENDATIONS - DETAILED ANALYSIS", "=")
    for i, analysis in enumerate(comparison_result['ranked'][:3], 1):
        print_detailed_scenario(analysis)
        if i < 3:
            print("\n" + "▼" * 80 + "\n")

    # Print key insights
    print_header("KEY INSIGHTS & RECOMMENDATIONS", "=")

    best = comparison_result['ranked'][0]
    second = comparison_result['ranked'][1]
    worst = comparison_result['ranked'][-1]

    print("\n1. BEST OVERALL SCENARIO:")
    print(f"   → {best['scenario_name']}")
    print(f"   • Recommendation Score: {best['recommendation_score']}/10")
    print(f"   • Net Position: {format_currency(best['financial_summary']['net_position'])}")
    print(f"   • Monthly Cost: {format_currency(best['financial_summary']['equivalent_monthly_cost'])}")
    print(f"   • Functionality: {best['functionality_score']}/10")

    print("\n2. RUNNER-UP:")
    print(f"   → {second['scenario_name']}")
    print(f"   • Recommendation Score: {second['recommendation_score']}/10")
    print(f"   • Trade-off: ", end="")
    if second['functionality_score'] > best['functionality_score']:
        print(f"Higher functionality (+{second['functionality_score'] - best['functionality_score']:.1f}) but costs more")
    else:
        print(f"Lower cost but reduced functionality (-{best['functionality_score'] - second['functionality_score']:.1f})")

    print("\n3. TIMING ANALYSIS:")
    keep_6mo = next(a for a in comparison_result['analyses'] if 'Keep Tesla 6mo' in a['scenario_name'])
    sell_now_same = next((a for a in comparison_result['analyses']
                          if 'Sell Now → Lexus GX' in a['scenario_name']), None)

    if sell_now_same:
        credit_benefit = keep_6mo['financial_summary']['credits']
        depreciation_cost = estimate_tesla_trade_in(0) - estimate_tesla_trade_in(6)
        net_benefit = credit_benefit - depreciation_cost

        print(f"   • Waiting 6 months for credits: ${credit_benefit:,.0f}")
        print(f"   • Tesla depreciation in 6 months: ${depreciation_cost:,.0f}")
        print(f"   • Net benefit of waiting: {format_currency(net_benefit)}")

        if net_benefit > 1000:
            print(f"   → RECOMMENDATION: Wait 6 months to capture credits")
        else:
            print(f"   → Waiting provides minimal benefit; sell now if ready to switch")

    print("\n4. VALUE RETENTION LEADERS:")
    # Find vehicles with best value retention
    retention_data = []
    for analysis in comparison_result['analyses']:
        for dep in analysis['depreciation_analysis']:
            retention_pct = (dep['future_value'] / dep['current_value']) * 100
            retention_data.append((dep['vehicle'], retention_pct))

    retention_data.sort(key=lambda x: x[1], reverse=True)
    for vehicle, retention in retention_data[:3]:
        print(f"   • {vehicle}: {retention:.1f}% value retention")

    print("\n5. PRACTICAL RECOMMENDATIONS:")
    print("   • Toyota/Lexus products show superior value retention")
    print("   • Adding a trailer increases functionality but adds cost")
    print("   • Dual-vehicle ownership has storage costs but maximum flexibility")
    print("   • Your high mileage (20k/year) favors reliable, fuel-efficient vehicles")

    # Export to JSON
    print_section("Exporting detailed data")
    output_file = "vehicle_analysis_results.json"
    with open(output_file, 'w') as f:
        json.dump(comparison_result, f, indent=2, default=str)
    print(f"Detailed results exported to: {output_file}")

    print_header("ANALYSIS COMPLETE", "=")
    print(f"\nBest Scenario: {comparison_result['best_scenario']}")
    print("\nNext Steps:")
    print("  1. Review detailed analysis of top 3 scenarios above")
    print("  2. Consider test-driving recommended vehicles")
    print("  3. Get actual trade-in quotes for your Tesla")
    print("  4. Evaluate insurance quotes for target vehicles")
    print("  5. Check availability and pricing in Bay Area market")


if __name__ == "__main__":
    main()
