#!/usr/bin/env python3
"""
Car Valuation Dashboard
Interactive web-based interface for the car valuation system
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import (
    DatabaseManager, VehicleRepository, MarketPriceRepository,
    ProblemRepository, DriverFitRepository, MarketPrice
)
from scoring_engine import VehicleScorer, UserPreferences
from recommendation_engine import RecommendationEngine
from market_analysis import MarketAnalyzer


# Page configuration
st.set_page_config(
    page_title="Car Valuation Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #1f77b4;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .deal-excellent { color: #28a745; font-weight: bold; }
    .deal-good { color: #5cb85c; font-weight: bold; }
    .deal-fair { color: #f0ad4e; font-weight: bold; }
    .deal-poor { color: #d9534f; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


# Initialize database connections
@st.cache_resource
def init_db():
    db = DatabaseManager()
    return {
        'db': db,
        'vehicle_repo': VehicleRepository(db),
        'price_repo': MarketPriceRepository(db),
        'problem_repo': ProblemRepository(db),
        'fit_repo': DriverFitRepository(db),
        'scorer': VehicleScorer(db),
        'recommender': RecommendationEngine(db),
        'market_analyzer': MarketAnalyzer(db)
    }


repos = init_db()


def main():
    """Main dashboard"""

    # Sidebar navigation
    st.sidebar.title("🚗 Navigation")

    page = st.sidebar.radio(
        "Select Page",
        [
            "🏠 Home",
            "🔍 Find Vehicles",
            "💎 Deal Finder",
            "📊 Market Analysis",
            "⚠️ Problem Database",
            "📏 Tall Driver Fit",
            "➕ Add Listing",
            "📈 Compare Vehicles"
        ]
    )

    # Route to pages
    if page == "🏠 Home":
        show_home()
    elif page == "🔍 Find Vehicles":
        show_vehicle_finder()
    elif page == "💎 Deal Finder":
        show_deal_finder()
    elif page == "📊 Market Analysis":
        show_market_analysis()
    elif page == "⚠️ Problem Database":
        show_problems()
    elif page == "📏 Tall Driver Fit":
        show_tall_driver_fit()
    elif page == "➕ Add Listing":
        show_add_listing()
    elif page == "📈 Compare Vehicles":
        show_comparison()


def show_home():
    """Home page with overview"""

    st.markdown('<h1 class="main-header">🚗 Car Valuation Dashboard</h1>', unsafe_allow_html=True)

    st.markdown("""
    ### Welcome to your comprehensive car valuation system!

    This dashboard helps you find the best vehicle deals by analyzing:
    - **Fair market values** across different regions
    - **Vehicle reliability** and known problems
    - **Total cost of ownership** over 3 years
    - **Driver fit** especially for tall drivers (6'3"+)
    - **Market trends** and arbitrage opportunities
    """)

    # Quick stats
    col1, col2, col3, col4 = st.columns(4)

    vehicles = repos['vehicle_repo'].find_vehicles()
    listings = repos['price_repo'].get_listings()

    with col1:
        st.metric("🚙 Vehicles in Database", len(vehicles))

    with col2:
        st.metric("📋 Active Listings", len([l for l in listings if not l.get('sold')]))

    with col3:
        st.metric("✅ Sold Listings", len([l for l in listings if l.get('sold')]))

    with col4:
        avg_price = sum(l['asking_price'] for l in listings) / len(listings) if listings else 0
        st.metric("💰 Avg Asking Price", f"${avg_price:,.0f}")

    # Market heat
    st.markdown("---")
    st.subheader("📈 Market Conditions")

    heat = repos['market_analyzer'].calculate_market_heat()

    if 'error' not in heat:
        col1, col2 = st.columns([1, 2])

        with col1:
            st.metric("Market Condition", heat['market_condition'])
            st.metric("Sell-Through Rate", f"{heat['sell_through_rate']}%")

        with col2:
            st.info(f"**Buyer Advice:** {heat['buyer_advice']}")

            # Supply chart
            supply_df = pd.DataFrame([
                {'Vehicle': k, 'Listings': v}
                for k, v in heat['supply_by_vehicle'].items()
            ])

            fig = px.bar(supply_df, x='Vehicle', y='Listings',
                        title="Current Inventory by Vehicle")
            st.plotly_chart(fig, use_container_width=True)

    # Recent listings
    st.markdown("---")
    st.subheader("🆕 Recent Listings")

    if listings:
        recent = sorted(listings, key=lambda x: x.get('listing_date', ''), reverse=True)[:5]

        for listing in recent:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

                with col1:
                    st.write(f"**{listing['year']} {listing['make']} {listing['model']}**")

                with col2:
                    st.write(f"${listing['asking_price']:,.0f}")

                with col3:
                    st.write(f"{listing['mileage']:,} mi")

                with col4:
                    st.write(listing.get('city', 'N/A'))


def show_vehicle_finder():
    """Find vehicles based on preferences"""

    st.title("🔍 Find Your Ideal Vehicle")

    st.markdown("### Set Your Preferences")

    col1, col2 = st.columns(2)

    with col1:
        budget = st.number_input("Maximum Budget ($)",
                                 min_value=10000, max_value=150000,
                                 value=70000, step=5000)

        height_ft = st.number_input("Your Height (feet)", min_value=4, max_value=7, value=6)
        height_in = st.number_input("Additional Inches", min_value=0, max_value=11, value=3)
        driver_height = height_ft * 12 + height_in

        max_mileage = st.number_input("Max Mileage",
                                      min_value=0, max_value=200000,
                                      value=50000, step=10000)

    with col2:
        use_case = st.selectbox(
            "Primary Use Case",
            ["Outdoor Adventures", "Daily Commute", "Family Hauler", "Balanced"]
        )

        min_cargo = st.number_input("Min Cargo (cu ft)", min_value=0, value=60)
        min_towing = st.number_input("Min Towing (lbs)", min_value=0, value=5000, step=500)
        require_4wd = st.checkbox("Require 4WD/AWD", value=True)

    # Set preferences based on use case
    if use_case == "Outdoor Adventures":
        weights = {
            'weight_features': 0.30,
            'weight_reliability': 0.25,
            'weight_comfort': 0.20,
            'weight_price': 0.15,
            'weight_resale': 0.05,
            'weight_maintenance': 0.05
        }
    elif use_case == "Daily Commute":
        weights = {
            'weight_maintenance': 0.30,
            'weight_price': 0.25,
            'weight_reliability': 0.20,
            'weight_comfort': 0.15,
            'weight_features': 0.05,
            'weight_resale': 0.05
        }
    elif use_case == "Family Hauler":
        weights = {
            'weight_comfort': 0.30,
            'weight_features': 0.25,
            'weight_reliability': 0.20,
            'weight_price': 0.15,
            'weight_resale': 0.05,
            'weight_maintenance': 0.05
        }
    else:  # Balanced
        weights = {
            'weight_price': 0.25,
            'weight_reliability': 0.25,
            'weight_comfort': 0.20,
            'weight_features': 0.15,
            'weight_resale': 0.10,
            'weight_maintenance': 0.05
        }

    prefs = UserPreferences(
        budget_max=budget,
        driver_height=driver_height,
        min_cargo_cuft=min_cargo,
        min_towing_lbs=min_towing,
        require_4wd=require_4wd,
        require_tall_driver_suitable=driver_height >= 75,
        max_mileage=max_mileage,
        **weights
    )

    if st.button("🔍 Find Matches", type="primary"):
        with st.spinner("Searching for matches..."):
            matches = repos['recommender'].find_best_matches(prefs, limit=10)

        if not matches:
            st.warning("No vehicles found matching your criteria. Try adjusting your requirements.")
        else:
            st.success(f"Found {len(matches)} matching vehicles!")

            for i, match in enumerate(matches, 1):
                veh = match['score']['vehicle_details']
                listing = match['listing']
                score = match['score']

                with st.expander(
                    f"#{i}. {veh['year']} {veh['make']} {veh['model']} {veh['trim']} - Score: {score['total_score']}/100",
                    expanded=(i <= 3)
                ):
                    col1, col2 = st.columns([1, 2])

                    with col1:
                        st.metric("Asking Price", f"${listing['asking_price']:,.0f}")
                        st.metric("Fair Value", f"${score['fair_market_value']:,.0f}")
                        st.metric("Mileage", f"{listing['mileage']:,}")
                        st.metric("Condition", listing.get('condition', 'Good'))

                        deal_class = score['deal_quality']
                        if "Excellent" in deal_class:
                            st.markdown(f'<p class="deal-excellent">{deal_class}</p>', unsafe_allow_html=True)
                        elif "Good" in deal_class:
                            st.markdown(f'<p class="deal-good">{deal_class}</p>', unsafe_allow_html=True)
                        elif "Fair" in deal_class:
                            st.markdown(f'<p class="deal-fair">{deal_class}</p>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<p class="deal-poor">{deal_class}</p>', unsafe_allow_html=True)

                    with col2:
                        st.markdown(f"**Recommendation:** {score['recommendation']}")

                        # Score breakdown chart
                        breakdown_df = pd.DataFrame([
                            {'Category': k.capitalize(), 'Score': v}
                            for k, v in score['scores_breakdown'].items()
                        ])

                        fig = px.bar(breakdown_df, x='Score', y='Category',
                                    orientation='h',
                                    title="Score Breakdown",
                                    color='Score',
                                    color_continuous_scale='RdYlGn',
                                    range_color=[0, 100])
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)

                        st.markdown(f"**Location:** {listing.get('city', 'N/A')}, {listing.get('region', 'N/A')}")


def show_deal_finder():
    """Find underpriced deals"""

    st.title("💎 Deal Finder")

    st.markdown("""
    Find vehicles priced significantly below market average.
    These represent the best opportunities for immediate purchase.
    """)

    threshold = st.slider(
        "Minimum Discount (%)",
        min_value=5,
        max_value=25,
        value=10,
        step=5
    )

    deals = repos['market_analyzer'].find_underpriced_listings(threshold_pct=threshold)

    if not deals:
        st.info(f"No listings found at least {threshold}% below market average.")
    else:
        st.success(f"Found {len(deals)} underpriced listings!")

        # Summary stats
        total_savings = sum(d['savings'] for d in deals)
        avg_discount = sum(d['savings_pct'] for d in deals) / len(deals)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Opportunities", len(deals))
        with col2:
            st.metric("Total Potential Savings", f"${total_savings:,.0f}")
        with col3:
            st.metric("Avg Discount", f"{avg_discount:.1f}%")

        # Deals table
        st.markdown("---")

        for deal in deals:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 2])

                with col1:
                    st.markdown(f"### {deal['vehicle']}")
                    st.write(f"**Location:** {deal['location']}")
                    st.write(f"**Condition:** {deal['condition']} | **Mileage:** {deal['mileage']:,}")

                with col2:
                    st.metric("Asking Price", f"${deal['asking_price']:,.0f}")
                    st.metric("Market Average", f"${deal['market_avg']:,.0f}")

                with col3:
                    st.metric("SAVINGS", f"${deal['savings']:,.0f}",
                             delta=f"-{deal['savings_pct']:.1f}%",
                             delta_color="inverse")
                    st.write(f"*Listing ID: {deal['listing_id']}*")

                st.markdown("---")


def show_market_analysis():
    """Market analysis and trends"""

    st.title("📊 Market Analysis")

    tab1, tab2, tab3 = st.tabs(["Regional Pricing", "Best Markets", "Price Trends"])

    with tab1:
        st.subheader("Regional Price Comparison")

        vehicles = repos['vehicle_repo'].find_vehicles()
        vehicle_options = [f"{v['year']} {v['make']} {v['model']}" for v in vehicles]

        if vehicle_options:
            selected = st.selectbox("Select Vehicle", vehicle_options)

            if selected:
                parts = selected.split()
                year = int(parts[0])
                make = parts[1]
                model = parts[2]

                result = repos['market_analyzer'].analyze_regional_pricing(make, model, year)

                if 'error' not in result:
                    # Regional stats
                    stats_data = []
                    for region, stats in result['regional_stats'].items():
                        stats_data.append({
                            'Region': region,
                            'Listings': stats['listing_count'],
                            'Avg Price': stats['avg_asking_price'],
                            'Median Price': stats['median_asking_price'],
                            'Min Price': stats['min_price'],
                            'Max Price': stats['max_price']
                        })

                    df = pd.DataFrame(stats_data)

                    # Price comparison chart
                    fig = px.bar(df, x='Region', y='Avg Price',
                                title=f"Average Price by Region - {result['vehicle']}",
                                color='Avg Price',
                                color_continuous_scale='Viridis')
                    st.plotly_chart(fig, use_container_width=True)

                    # Stats table
                    st.dataframe(df, use_container_width=True)

                    # Arbitrage opportunity
                    if result['arbitrage_opportunity']:
                        st.success("🎯 Arbitrage Opportunity Detected!")
                        arb = result['arbitrage_opportunity']

                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Buy from", arb['buy_from'])
                            st.metric("Average Price", f"${arb['buy_price']:,.0f}")

                        with col2:
                            st.metric("Sell to", arb['sell_to'])
                            st.metric("Average Price", f"${arb['sell_price']:,.0f}")

                        st.metric("Potential Profit",
                                 f"${arb['potential_profit']:,.0f}",
                                 delta=f"{arb['profit_percentage']}%")
                else:
                    st.info(result['error'])

    with tab2:
        st.subheader("Best Markets for Buyers & Sellers")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🛒 Best Markets to BUY From")
            st.caption("(Lowest average prices)")

            buy_markets = repos['market_analyzer'].find_best_buy_markets(limit=5)

            for i, market in enumerate(buy_markets, 1):
                st.write(f"**{i}. {market['region']}**")
                st.write(f"   Avg: ${market['avg_price']:,.0f} | Listings: {market['listing_count']}")

        with col2:
            st.markdown("### 💰 Best Markets to SELL To")
            st.caption("(Highest average prices)")

            sell_markets = repos['market_analyzer'].find_best_sell_markets(limit=5)

            for i, market in enumerate(sell_markets, 1):
                st.write(f"**{i}. {market['region']}**")
                st.write(f"   Avg: ${market['avg_price']:,.0f} | Listings: {market['listing_count']}")

    with tab3:
        st.subheader("Price Trends")
        st.info("Price trend analysis requires more historical data. Add more listings to see trends over time.")


def show_problems():
    """Vehicle problems database"""

    st.title("⚠️ Vehicle Problems & Reliability")

    col1, col2 = st.columns(2)

    with col1:
        make = st.text_input("Make (e.g., Toyota)")

    with col2:
        model = st.text_input("Model (e.g., Tacoma)")

    year = st.text_input("Year (optional, leave blank for all)")

    if st.button("Search Problems"):
        year_int = int(year) if year else None
        problems = repos['problem_repo'].get_problems(make, model, year_int)

        if not problems:
            st.success(f"✅ No known problems for {make} {model}" + (f" {year}" if year else ""))
            st.info("This could mean excellent reliability or limited data in the database.")
        else:
            st.warning(f"Found {len(problems)} known problems")

            # Group by severity
            critical = [p for p in problems if p['severity'] == 'critical']
            major = [p for p in problems if p['severity'] == 'major']
            moderate = [p for p in problems if p['severity'] == 'moderate']
            minor = [p for p in problems if p['severity'] == 'minor']

            if critical:
                st.error(f"🚨 {len(critical)} Critical Problems")
            if major:
                st.warning(f"⚠️ {len(major)} Major Problems")
            if moderate:
                st.info(f"ℹ️ {len(moderate)} Moderate Problems")
            if minor:
                st.success(f"✓ {len(minor)} Minor Problems")

            # Display problems
            for problem in problems:
                severity_emoji = {
                    'critical': '🚨',
                    'major': '⚠️',
                    'moderate': 'ℹ️',
                    'minor': '✓'
                }

                years = f"{problem['year_start']}-{problem['year_end']}" if problem['year_start'] != problem['year_end'] else str(problem['year_start'])

                with st.expander(
                    f"{severity_emoji.get(problem['severity'], '•')} {years} | {problem['problem_category']} | {problem['severity'].upper()}"
                ):
                    st.write(problem['problem_description'])

                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Frequency:** {problem['frequency']}")
                        if problem['avg_repair_cost'] > 0:
                            st.write(f"**Avg Repair Cost:** ${problem['avg_repair_cost']:,.0f}")

                    with col2:
                        if problem['has_tsb']:
                            st.write(f"**TSB:** {problem['tsb_number']}")
                        if problem['has_recall']:
                            st.write(f"**RECALL:** {problem['recall_number']}")

                    if problem['notes']:
                        st.info(problem['notes'])


def show_tall_driver_fit():
    """Tall driver analysis"""

    st.title("📏 Tall Driver Vehicle Fit")

    st.markdown("""
    Find vehicles suitable for tall drivers (6'3"+) with excellent comfort and space.
    """)

    col1, col2 = st.columns(2)

    with col1:
        height_ft = st.number_input("Height (feet)", min_value=5, max_value=7, value=6)
        height_in = st.number_input("Additional inches", min_value=0, max_value=11, value=3)

    with col2:
        min_comfort = st.slider("Minimum Comfort Score", min_value=1, max_value=10, value=7)

    driver_height = height_ft * 12 + height_in

    if st.button("Find Suitable Vehicles"):
        suitable = repos['fit_repo'].find_suitable_vehicles(driver_height, min_comfort)

        if not suitable:
            st.warning(f"No vehicles found suitable for {driver_height}\" height with {min_comfort}+ comfort score.")
        else:
            st.success(f"Found {len(suitable)} suitable vehicles for {height_ft}'{height_in}\" driver")

            for veh in suitable:
                with st.expander(
                    f"{veh['year']} {veh['make']} {veh['model']} {veh.get('trim', '')} - Comfort: {veh['seat_comfort_score']}/10"
                ):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Seat Comfort", f"{veh['seat_comfort_score']}/10")
                        st.metric("Adjustability", f"{veh['seat_adjustability_score']}/10")

                    with col2:
                        st.metric("Front Legroom", f"{veh['legroom_front_in']}\"")
                        st.metric("Rear Legroom", f"{veh['legroom_rear_in']}\"")

                    with col3:
                        st.metric("Front Headroom", f"{veh['headroom_front_in']}\"")
                        st.metric("Rear Headroom", f"{veh['headroom_rear_in']}\"")

                    if veh['tall_driver_notes']:
                        st.info(f"**Notes:** {veh['tall_driver_notes']}")


def show_add_listing():
    """Add new listing form"""

    st.title("➕ Add New Listing")

    vehicles = repos['vehicle_repo'].find_vehicles()

    if not vehicles:
        st.error("No vehicles in database. Please import vehicles first.")
        return

    vehicle_options = [f"{v['year']} {v['make']} {v['model']} {v.get('trim', '')}" for v in vehicles]

    with st.form("add_listing_form"):
        st.subheader("Vehicle Selection")

        selected = st.selectbox("Select Vehicle", vehicle_options)

        st.subheader("Listing Details")

        col1, col2 = st.columns(2)

        with col1:
            asking_price = st.number_input("Asking Price ($)", min_value=0, value=50000, step=1000)
            mileage = st.number_input("Mileage", min_value=0, value=10000, step=1000)
            condition = st.selectbox("Condition", ["excellent", "good", "fair", "poor"])
            city = st.text_input("City")

        with col2:
            region = st.text_input("Region", value="Bay Area")
            has_leather = st.checkbox("Has Leather")
            has_tow = st.checkbox("Has Tow Package")
            has_nav = st.checkbox("Has Navigation")

        submitted = st.form_submit_button("Add Listing", type="primary")

        if submitted:
            # Find vehicle ID
            vehicle_id = None
            for v in vehicles:
                veh_str = f"{v['year']} {v['make']} {v['model']} {v.get('trim', '')}"
                if veh_str == selected:
                    vehicle_id = v['id']
                    break

            if vehicle_id:
                listing = MarketPrice(
                    vehicle_id=vehicle_id,
                    listing_date="2024-01-29",
                    mileage=mileage,
                    asking_price=asking_price,
                    condition=condition,
                    city=city,
                    region=region,
                    has_leather=has_leather,
                    has_tow_package=has_tow,
                    has_nav=has_nav,
                    source="dashboard"
                )

                listing_id = repos['price_repo'].add_listing(listing)
                st.success(f"✅ Listing added successfully! ID: {listing_id}")
                st.balloons()
            else:
                st.error("Could not find selected vehicle")


def show_comparison():
    """Compare multiple vehicles"""

    st.title("📈 Vehicle Comparison")

    vehicles = repos['vehicle_repo'].find_vehicles()
    vehicle_options = [f"{v['year']} {v['make']} {v['model']}" for v in vehicles]

    selected = st.multiselect(
        "Select vehicles to compare (up to 4)",
        vehicle_options,
        max_selections=4
    )

    if len(selected) >= 2:
        vehicle_ids = []
        for sel in selected:
            for v in vehicles:
                if f"{v['year']} {v['make']} {v['model']}" == sel:
                    vehicle_ids.append(v['id'])
                    break

        # Get TCO comparison
        tco_result = repos['recommender'].compare_ownership_scenarios(vehicle_ids, budget=100000, years=3)

        if tco_result['vehicles_compared'] > 0:
            st.subheader("3-Year Total Cost of Ownership Comparison")

            # Create comparison dataframe
            comp_df = pd.DataFrame(tco_result['comparisons'])

            # TCO Chart
            fig = px.bar(comp_df, x='vehicle', y='total_cost_of_ownership',
                        title="Total Cost of Ownership (3 Years)",
                        labels={'total_cost_of_ownership': 'Total Cost ($)', 'vehicle': 'Vehicle'},
                        color='total_cost_of_ownership',
                        color_continuous_scale='RdYlGn_r')
            st.plotly_chart(fig, use_container_width=True)

            # Detailed breakdown
            st.subheader("Cost Breakdown")

            for comp in tco_result['comparisons']:
                with st.expander(comp['vehicle']):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric("Purchase Price", f"${comp['avg_purchase_price']:,.0f}")
                        st.metric("Fuel Cost", f"${comp['fuel_cost']:,.0f}")
                        st.metric("Maintenance", f"${comp['maintenance_cost']:,.0f}")
                        st.metric("Insurance", f"${comp['insurance_cost']:,.0f}")

                    with col2:
                        st.metric("Depreciation", f"${comp['depreciation']:,.0f}")
                        st.metric("Estimated End Value", f"${comp['estimated_end_value']:,.0f}")
                        st.metric("TOTAL TCO", f"${comp['total_cost_of_ownership']:,.0f}")
                        st.metric("Monthly Equivalent", f"${comp['monthly_equivalent']:,.0f}/mo")


if __name__ == "__main__":
    main()
