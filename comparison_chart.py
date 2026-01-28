"""
Comparison Chart Generator
Creates visual comparison charts for quick decision-making
"""

import json


def load_analysis_results():
    """Load the full analysis results"""
    try:
        with open('vehicle_analysis_results.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: Run analysis.py first to generate results")
        return None


def create_bar_chart(value: float, max_value: float, width: int = 40, char: str = "█") -> str:
    """Create a text-based bar chart"""
    if max_value == 0:
        return ""
    filled = int((abs(value) / abs(max_value)) * width)
    return char * filled


def print_cost_comparison_chart():
    """Print visual comparison of costs across scenarios"""
    results = load_analysis_results()
    if not results:
        return

    print("\n" + "="*90)
    print("MONTHLY COST COMPARISON".center(90))
    print("="*90 + "\n")

    # Get comparison data
    scenarios = results['comparison_summary']

    # Sort by monthly cost (absolute value)
    scenarios_sorted = sorted(scenarios, key=lambda x: abs(x['monthly_cost']))

    max_cost = max(abs(s['monthly_cost']) for s in scenarios)

    for scenario in scenarios_sorted:
        cost = scenario['monthly_cost']
        name = scenario['scenario'][:40]

        # Create bar
        bar = create_bar_chart(cost, max_cost, width=50)

        print(f"{name:<42} ${abs(cost):>6.0f}/mo {bar}")

    print("\n" + "="*90 + "\n")


def print_functionality_comparison_chart():
    """Print visual comparison of functionality scores"""
    results = load_analysis_results()
    if not results:
        return

    print("\n" + "="*90)
    print("FUNCTIONALITY SCORE COMPARISON (Higher = Better)".center(90))
    print("="*90 + "\n")

    scenarios = results['comparison_summary']
    scenarios_sorted = sorted(scenarios, key=lambda x: x['functionality_score'], reverse=True)

    for scenario in scenarios_sorted:
        score = scenario['functionality_score']
        name = scenario['scenario'][:40]
        bar = create_bar_chart(score, 10, width=50, char="█")

        print(f"{name:<42} {score:>4.1f}/10 {bar}")

    print("\n" + "="*90 + "\n")


def print_recommendation_comparison_chart():
    """Print visual comparison of overall recommendation scores"""
    results = load_analysis_results()
    if not results:
        return

    print("\n" + "="*90)
    print("OVERALL RECOMMENDATION SCORE (Higher = Better)".center(90))
    print("="*90 + "\n")

    scenarios = results['ranked']  # Already sorted by recommendation score

    for i, scenario in enumerate(scenarios, 1):
        score = scenario['recommendation_score']
        name = scenario['scenario_name'][:40]
        bar = create_bar_chart(score, 10, width=50, char="█")

        rank = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i:>2}"

        print(f"{rank} {name:<39} {score:>4.1f}/10 {bar}")

    print("\n" + "="*90 + "\n")


def print_net_position_chart():
    """Print visual comparison of net financial positions"""
    results = load_analysis_results()
    if not results:
        return

    print("\n" + "="*90)
    print("NET FINANCIAL POSITION (Less Negative = Better)".center(90))
    print("="*90 + "\n")

    scenarios = results['comparison_summary']
    scenarios_sorted = sorted(scenarios, key=lambda x: x['net_position'], reverse=True)

    max_position = max(abs(s['net_position']) for s in scenarios)

    for scenario in scenarios_sorted:
        position = scenario['net_position']
        name = scenario['scenario'][:40]
        bar = create_bar_chart(position, max_position, width=40)

        # Color code: less negative is better
        symbol = "✓" if position > -10000 else "○"

        print(f"{symbol} {name:<39} ${position:>8,.0f} {bar}")

    print("\n" + "="*90 + "\n")


def print_value_retention_chart():
    """Print value retention percentages"""
    results = load_analysis_results()
    if not results:
        return

    print("\n" + "="*90)
    print("VALUE RETENTION AFTER 3 YEARS (Higher = Better)".center(90))
    print("="*90 + "\n")

    retention_data = []

    for analysis in results['analyses']:
        for dep in analysis['depreciation_analysis']:
            retention_pct = (dep['future_value'] / dep['current_value']) * 100
            retention_data.append({
                'vehicle': dep['vehicle'],
                'retention': retention_pct,
                'scenario': analysis['scenario_name']
            })

    # Remove duplicates by vehicle name
    seen = set()
    unique_data = []
    for item in retention_data:
        if item['vehicle'] not in seen:
            seen.add(item['vehicle'])
            unique_data.append(item)

    unique_data.sort(key=lambda x: x['retention'], reverse=True)

    for item in unique_data:
        vehicle = item['vehicle'][:45]
        retention = item['retention']
        bar = create_bar_chart(retention, 100, width=40, char="█")

        symbol = "★" if retention > 70 else "◆" if retention > 60 else "○"

        print(f"{symbol} {vehicle:<47} {retention:>5.1f}% {bar}")

    print("\n" + "="*90)
    print("★ = Excellent (>70%)  ◆ = Good (>60%)  ○ = Average")
    print("="*90 + "\n")


def print_decision_matrix():
    """Print a simplified decision matrix"""
    results = load_analysis_results()
    if not results:
        return

    print("\n" + "="*100)
    print("DECISION MATRIX - TOP 5 SCENARIOS".center(100))
    print("="*100 + "\n")

    print(f"{'Scenario':<35} {'Overall':<10} {'Practical':<10} {'Financial':<12} {'Monthly':<12}")
    print(f"{'':35} {'Score':<10} {'Score':<10} {'Position':<12} {'Cost':<12}")
    print("-"*100)

    top_5 = results['ranked'][:5]

    for scenario in top_5:
        name = scenario['scenario_name'][:34]
        overall = scenario['recommendation_score']
        practical = scenario['functionality_score']
        financial = scenario['financial_summary']['net_position']
        monthly = scenario['financial_summary']['equivalent_monthly_cost']

        # Generate simple indicators
        overall_indicator = "●●●" if overall >= 6 else "●●○" if overall >= 5 else "●○○"
        practical_indicator = "●●●" if practical >= 7.5 else "●●○" if practical >= 7 else "●○○"
        financial_indicator = "●●●" if financial > -15000 else "●●○" if financial > -30000 else "●○○"

        print(f"{name:<35} {overall:>4.1f} {overall_indicator:<5} {practical:>4.1f} {practical_indicator:<5} "
              f"${financial:>7,.0f} {financial_indicator:<3} ${monthly:>6,.0f}/mo")

    print("\n" + "="*100)
    print("● = Good  ◐ = Moderate  ○ = Concern")
    print("="*100 + "\n")


def print_summary_table():
    """Print a comprehensive summary table"""
    results = load_analysis_results()
    if not results:
        return

    print("\n" + "="*120)
    print("COMPREHENSIVE VEHICLE COMPARISON SUMMARY".center(120))
    print("="*120 + "\n")

    print(f"{'Vehicle/Scenario':<38} {'Price':<12} {'Monthly':<10} {'Func':<8} {'Overall':<8} {'Status':<12}")
    print("-"*120)

    for analysis in results['ranked'][:8]:  # Top 8
        name = analysis['scenario_name'][:37]
        # Extract vehicle price from first vehicle in scenario
        vehicles = analysis['depreciation_analysis']
        price = vehicles[0]['current_value'] if vehicles else 0
        monthly = abs(analysis['financial_summary']['equivalent_monthly_cost'])
        func = analysis['functionality_score']
        overall = analysis['recommendation_score']

        # Status indicator
        if overall >= 6.5:
            status = "🟢 Excellent"
        elif overall >= 5.5:
            status = "🟡 Good"
        elif overall >= 4.5:
            status = "🟠 Fair"
        else:
            status = "🔴 Poor"

        print(f"{name:<38} ${price:>9,.0f} ${monthly:>7,.0f} {func:>6.1f} {overall:>6.1f}  {status:<12}")

    print("\n" + "="*120 + "\n")


def main():
    """Run all comparison charts"""
    print("\n" + "█"*100)
    print("VEHICLE OPTIMIZATION - VISUAL COMPARISON CHARTS")
    print("█"*100)

    print_recommendation_comparison_chart()
    print_functionality_comparison_chart()
    print_cost_comparison_chart()
    print_net_position_chart()
    print_value_retention_chart()
    print_decision_matrix()
    print_summary_table()

    print("\n" + "█"*100)
    print("CHART GENERATION COMPLETE")
    print("█"*100 + "\n")


if __name__ == "__main__":
    main()
