#!/usr/bin/env python3
"""
Car Valuation Dashboard
Interactive web-based interface for the car valuation system
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import urllib.parse
import numpy as np
from scipy.stats import linregress
from database import (
    DatabaseManager, VehicleRepository, MarketPriceRepository,
    ProblemRepository, DriverFitRepository, MarketPrice
)
from scoring_engine import VehicleScorer, UserPreferences
from recommendation_engine import RecommendationEngine
from market_analysis import MarketAnalyzer


def generate_fb_marketplace_link(vehicle_name: str, price: float, city: str = "", state: str = "") -> str:
    """Generate Facebook Marketplace search URL for a vehicle"""
    search_query = vehicle_name.replace(' ', '+')
    price_min = int(price * 0.95)
    price_max = int(price * 1.05)

    url = f"https://www.facebook.com/marketplace/search/?query={search_query}&minPrice={price_min}&maxPrice={price_max}"

    # Add location if available
    if city and state:
        location = f"{city}+{state}".replace(' ', '+')
        url += f"&exact=false"

    return url


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
    """Home page with multi-dimensional analysis"""

    st.markdown('<h1 class="main-header">🚗 Car Valuation Dashboard</h1>', unsafe_allow_html=True)

    st.markdown("""
    ### Welcome! Find the best vehicle deals with data-driven analysis.

    **📊 Go to Market Analysis → Multi-Dimensional Analysis** to:
    - Compare vehicles across Price, Mileage, Year, MPG, and Maintenance Cost
    - View regression analysis with R² scores and confidence bands
    - **Click on any data point** to open the Facebook Marketplace listing
    - Find statistically underpriced vehicles (below -2σ confidence band)
    """)

    # Quick stats
    col1, col2, col3 = st.columns(3)

    with repos['db'].get_connection() as conn:
        cursor = conn.execute("SELECT COUNT(DISTINCT make || model) FROM vehicles")
        unique_models = cursor.fetchone()[0]

        cursor = conn.execute("SELECT COUNT(*) FROM market_prices")
        total_listings = cursor.fetchone()[0]

        cursor = conn.execute("SELECT COUNT(*) FROM market_prices WHERE LENGTH(source_url) > 0")
        with_urls = cursor.fetchone()[0]

    with col1:
        st.metric("📊 Unique Models", unique_models)

    with col2:
        st.metric("📋 Total Listings", total_listings)

    with col3:
        st.metric("🔗 With Clickable URLs", f"{with_urls} ({100*with_urls//total_listings}%)")

    st.markdown("---")

    # Multi-dimensional analysis on home page
    st.subheader("📊 Interactive Vehicle Analysis")

    # Get unique models for filtering
    query = """
        SELECT DISTINCT v.make, v.model, COUNT(*) as listing_count
        FROM vehicles v
        JOIN market_prices mp ON v.id = mp.vehicle_id
        GROUP BY v.make, v.model
        HAVING listing_count >= 3
        ORDER BY listing_count DESC, v.make, v.model
    """

    with repos['db'].get_connection() as conn:
        cursor = conn.execute(query)
        models = cursor.fetchall()

    if not models:
        st.warning("Not enough data for analysis. Add more listings (need at least 3 per model).")
    else:
        # Model selector
        model_options = [f"{make} {model} ({count} listings)" for make, model, count in models]
        selected_model = st.selectbox("Select Model to Analyze", model_options, key="home_model")

        if selected_model:
            # Extract make and model from "Tesla Model Y (12 listings)" format
            clean_name = selected_model.split(" (")[0]  # Remove " (12 listings)"
            parts = clean_name.split(maxsplit=1)  # Split on first space only
            make = parts[0]  # "Tesla"
            model = parts[1] if len(parts) > 1 else parts[0]  # "Model Y"

            # Axis selection
            col1, col2 = st.columns(2)

            axis_options = {
                "Price ($)": "price",
                "Mileage": "mileage",
                "Year": "year",
                "MPG (Est.)": "mpg",
                "Annual Maintenance Cost (Est.)": "maintenance"
            }

            with col1:
                x_axis_label = st.selectbox("X-Axis", list(axis_options.keys()), index=1, key="home_x")  # Default: Mileage

            with col2:
                y_axis_label = st.selectbox("Y-Axis", list(axis_options.keys()), index=0, key="home_y")  # Default: Price

            x_axis = axis_options[x_axis_label]
            y_axis = axis_options[y_axis_label]

            # Optional color dimension
            color_by_label = st.selectbox("Color By (optional)", ["None"] + list(axis_options.keys()), index=3, key="home_color")  # Default: Year
            color_by = axis_options.get(color_by_label, None) if color_by_label != "None" else None

            # Fetch data for selected model
            query = """
                SELECT
                    v.year,
                    v.make,
                    v.model,
                    mp.asking_price as price,
                    mp.mileage,
                    mp.city,
                    mp.state,
                    mp.distance_miles,
                    mp.source_url,
                    mp.source,
                    mp.id
                FROM market_prices mp
                JOIN vehicles v ON mp.vehicle_id = v.id
                WHERE v.make = ? AND v.model = ?
                ORDER BY v.year DESC, mp.asking_price
            """

            with repos['db'].get_connection() as conn:
                cursor = conn.execute(query, (make, model))
                listings = cursor.fetchall()

            if not listings:
                st.warning(f"No listings found for {make} {model}")
            else:
                # Convert to dataframe
                df = pd.DataFrame(listings, columns=['year', 'make', 'model', 'price', 'mileage', 'city', 'state', 'distance', 'source_url', 'source', 'id'])

                # Mark owner's listing for highlighting
                df['is_owner'] = df['source'] == 'owner_listing'

                # Add calculated fields (MPG and maintenance)
                def estimate_mpg(row):
                    model_lower = row['model'].lower()
                    year = row['year']
                    if 'tacoma' in model_lower:
                        return 21 if year >= 2016 else 19
                    elif '4runner' in model_lower:
                        return 17 if year >= 2010 else 16
                    elif 'highlander' in model_lower:
                        return 24 if year >= 2020 else 21
                    elif 'sequoia' in model_lower:
                        return 15 if year >= 2018 else 14
                    elif 'tundra' in model_lower:
                        return 15 if year >= 2014 else 14
                    elif 'model y' in model_lower or 'model 3' in model_lower:
                        return 120
                    elif 'model s' in model_lower or 'model x' in model_lower:
                        return 105
                    elif 'gx' in model_lower:
                        return 16 if year >= 2014 else 15
                    elif 'lx' in model_lower:
                        return 14 if year >= 2016 else 13
                    elif 'rx' in model_lower:
                        return 25 if year >= 2020 else 22
                    elif 'es' in model_lower:
                        return 28 if year >= 2019 else 25
                    elif 'is' in model_lower:
                        return 26 if year >= 2014 else 24
                    else:
                        return 20

                def estimate_maintenance(row):
                    age = 2026 - row['year']
                    mileage = row['mileage']
                    model_lower = row['model'].lower()
                    if 'tesla' in model_lower or 'model' in model_lower:
                        base = 500
                    elif any(brand in model_lower for brand in ['lexus', 'gx', 'lx', 'rx', 'es', 'is', 'gs']):
                        base = 1000
                    else:
                        base = 800
                    age_factor = 1 + (age * 0.1)
                    if mileage > 150000:
                        mileage_factor = 1.5
                    elif mileage > 100000:
                        mileage_factor = 1.3
                    elif mileage > 50000:
                        mileage_factor = 1.1
                    else:
                        mileage_factor = 1.0
                    return int(base * age_factor * mileage_factor)

                df['mpg'] = df.apply(estimate_mpg, axis=1)
                df['maintenance'] = df.apply(estimate_maintenance, axis=1)

                # Create hover text with clickable URL
                df['hover_text'] = df.apply(
                    lambda row: f"<b>{row['year']} {row['make']} {row['model']}</b><br>" +
                               f"💰 Price: ${row['price']:,.0f}<br>" +
                               f"🛣️ Mileage: {row['mileage']:,}<br>" +
                               f"⛽ MPG: {row['mpg']}<br>" +
                               f"🔧 Maintenance/yr: ${row['maintenance']:,.0f}<br>" +
                               f"📍 Location: {row['city']}, {row['state']}" +
                               (f"<br>📏 Distance: {row['distance']:.0f}mi" if pd.notna(row['distance']) else "") +
                               (f"<br><br>🔗 <a href='{row['source_url']}' target='_blank' style='color:#1E88E5'>Click to view on Facebook</a>" if pd.notna(row['source_url']) and row['source_url'] else "<br><br>⚠️ No listing URL available"),
                    axis=1
                )

                # Calculate linear regression
                x_data = df[x_axis].values
                y_data = df[y_axis].values
                valid_mask = ~(np.isnan(x_data) | np.isnan(y_data))
                x_clean = x_data[valid_mask]
                y_clean = y_data[valid_mask]

                if len(x_clean) >= 3:
                    slope, intercept, r_value, p_value, std_err = linregress(x_clean, y_clean)
                    r_squared = r_value ** 2
                    x_range = np.linspace(x_clean.min(), x_clean.max(), 100)
                    y_pred = slope * x_range + intercept
                    y_fit = slope * x_clean + intercept
                    residuals = y_clean - y_fit
                    std_residuals = np.std(residuals)
                    y_pred_1std_upper = y_pred + std_residuals
                    y_pred_1std_lower = y_pred - std_residuals
                    y_pred_2std_upper = y_pred + 2 * std_residuals
                    y_pred_2std_lower = y_pred - 2 * std_residuals
                else:
                    r_squared = None
                    slope = None

                # Create scatter plot with URLs in customdata
                if color_by:
                    fig = px.scatter(
                        df, x=x_axis, y=y_axis, color=color_by,
                        hover_data={'hover_text': True, x_axis: False, y_axis: False, color_by: False},
                        custom_data=['source_url'],
                        title=f"{make} {model}: {y_axis_label} vs {x_axis_label}" + (f" (R² = {r_squared:.3f})" if r_squared is not None else ""),
                        labels={x_axis: x_axis_label, y_axis: y_axis_label, color_by: color_by_label},
                        color_continuous_scale='Viridis'
                    )
                else:
                    fig = px.scatter(
                        df, x=x_axis, y=y_axis,
                        hover_data={'hover_text': True, x_axis: False, y_axis: False},
                        custom_data=['source_url'],
                        title=f"{make} {model}: {y_axis_label} vs {x_axis_label}" + (f" (R² = {r_squared:.3f})" if r_squared is not None else ""),
                        labels={x_axis: x_axis_label, y_axis: y_axis_label}
                    )

                # Add regression bands
                if len(x_clean) >= 3:
                    fig.add_trace(go.Scatter(
                        x=np.concatenate([x_range, x_range[::-1]]),
                        y=np.concatenate([y_pred_2std_upper, y_pred_2std_lower[::-1]]),
                        fill='toself', fillcolor='rgba(128, 128, 128, 0.15)',
                        line=dict(color='rgba(255,255,255,0)'),
                        hoverinfo='skip', showlegend=True, name='±2σ (95% confidence)'
                    ))
                    fig.add_trace(go.Scatter(
                        x=np.concatenate([x_range, x_range[::-1]]),
                        y=np.concatenate([y_pred_1std_upper, y_pred_1std_lower[::-1]]),
                        fill='toself', fillcolor='rgba(128, 128, 128, 0.25)',
                        line=dict(color='rgba(255,255,255,0)'),
                        hoverinfo='skip', showlegend=True, name='±1σ (68% confidence)'
                    ))
                    fig.add_trace(go.Scatter(
                        x=x_range, y=y_pred, mode='lines',
                        line=dict(color='red', width=2, dash='dash'),
                        name=f'Linear Fit (R²={r_squared:.3f})',
                        hovertemplate=f'y = {slope:.2f}x + {intercept:.2f}<extra></extra>'
                    ))

                # Highlight owner's listing if present
                owner_df = df[df['is_owner']]
                if not owner_df.empty:
                    fig.add_trace(go.Scatter(
                        x=owner_df[x_axis],
                        y=owner_df[y_axis],
                        mode='markers',
                        marker=dict(size=20, color='gold', symbol='star', line=dict(color='darkgoldenrod', width=2)),
                        name='YOUR LISTING',
                        customdata=owner_df['source_url'].values.reshape(-1, 1),
                        hovertemplate='<b>YOUR LISTING</b><br>%{customdata[0]}<extra></extra>',
                        showlegend=True
                    ))

                fig.update_traces(hovertemplate='%{customdata[0]}<extra></extra>', selector=dict(mode='markers', name=None))
                fig.update_layout(height=600, showlegend=True,
                                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))

                # Add click event handler to open URLs (client-side, no page reload)
                st.info("💡 **Click any dot on the chart to open the listing on Facebook Marketplace**")

                # Generate unique ID for this chart
                chart_id = f"chart_{hash(make + model)}"

                # Convert figure to HTML with custom click handler
                plot_html = fig.to_html(include_plotlyjs='cdn', div_id=chart_id)

                # Add JavaScript to handle clicks
                custom_html = f"""
                {plot_html}
                <script>
                    document.getElementById('{chart_id}').on('plotly_click', function(data) {{
                        var point = data.points[0];
                        if (point.customdata && point.customdata[0]) {{
                            window.open(point.customdata[0], '_blank');
                        }}
                    }});
                </script>
                """

                components.html(custom_html, height=650, scrolling=False)

                # Quick stats
                if len(x_clean) >= 3 and r_squared is not None:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("R²", f"{r_squared:.3f}")
                    with col2:
                        st.metric("Listings", len(df))
                    with col3:
                        nearby = df[df['distance'] <= 100].shape[0] if 'distance' in df.columns else 0
                        st.metric("Within 100mi", nearby)
                    with col4:
                        st.metric("Avg Price", f"${df['price'].mean():,.0f}")

                # Clickable listings table
                st.markdown("---")
                st.subheader("📋 View Listings")

                # Prepare table data
                table_df = df[['year', 'make', 'model', 'price', 'mileage', 'city', 'state', 'distance', 'source_url']].copy()
                table_df = table_df.sort_values('price')
                table_df['price'] = table_df['price'].apply(lambda x: f"${x:,.0f}")
                table_df['mileage'] = table_df['mileage'].apply(lambda x: f"{x:,}")
                table_df['distance'] = table_df['distance'].apply(lambda x: f"{x:.0f}mi" if pd.notna(x) else "N/A")

                # Create display dataframe with link column
                display_df = table_df[['year', 'make', 'model', 'price', 'mileage', 'city', 'state', 'distance']].copy()
                display_df.columns = ['Year', 'Make', 'Model', 'Price', 'Mileage', 'City', 'State', 'Distance']

                # Display table with clickable links
                for idx, row in table_df.iterrows():
                    with st.expander(f"{row['year']} {row['make']} {row['model']} - {row['price']} @ {row['mileage']} ({row['city']}, {row['state']})"):
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.write(f"**Location:** {row['city']}, {row['state']}")
                            if pd.notna(row['distance']):
                                st.write(f"**Distance:** {row['distance']}")
                        with col_b:
                            if pd.notna(row['source_url']) and row['source_url']:
                                st.link_button("🔗 View on Facebook", row['source_url'], use_container_width=True)
                            else:
                                st.button("⚠️ No URL", disabled=True, use_container_width=True)


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

        max_distance = st.number_input("Max Distance (miles)",
                                       min_value=0, max_value=500,
                                       value=100, step=25,
                                       help="From Santa Cruz / San Jose")

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
            matches = repos['recommender'].find_best_matches(prefs, limit=50)  # Get more, then filter

            # Filter by distance
            if matches and max_distance < 500:
                filtered_matches = []
                for match in matches:
                    listing = match['listing']
                    # Get distance from database
                    distance_query = "SELECT distance_miles FROM market_prices WHERE id = ?"
                    with repos['db'].get_connection() as conn:
                        cursor = conn.execute(distance_query, (listing['id'],))
                        result = cursor.fetchone()
                        distance = result[0] if result and result[0] is not None else None

                    if distance is not None and distance <= max_distance:
                        match['distance'] = distance
                        filtered_matches.append(match)
                    elif distance is None:  # Include unknowns
                        match['distance'] = None
                        filtered_matches.append(match)

                # Sort by score, then by distance
                filtered_matches.sort(key=lambda x: (-x['score']['total_score'], x['distance'] if x['distance'] is not None else 9999))
                matches = filtered_matches[:10]  # Take top 10
            else:
                # Add distance info even if not filtering
                for match in matches:
                    listing = match['listing']
                    distance_query = "SELECT distance_miles FROM market_prices WHERE id = ?"
                    with repos['db'].get_connection() as conn:
                        cursor = conn.execute(distance_query, (listing['id'],))
                        result = cursor.fetchone()
                        distance = result[0] if result and result[0] is not None else None
                    match['distance'] = distance

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

                        location_text = f"**Location:** {listing.get('city', 'N/A')}, {listing.get('region', 'N/A')}"
                        if match.get('distance') is not None:
                            location_text += f" ({match['distance']:.0f} miles)"
                        st.markdown(location_text)

                        # Show actual listing URL with source indicator
                        if listing.get('source_url'):
                            st.markdown(f"📍 **Source:** Facebook Marketplace")
                            st.markdown(f"🔗 [View Listing]({listing['source_url']})")
                        else:
                            vehicle_name = f"{veh['year']} {veh['make']} {veh['model']}"
                            fb_search_url = generate_fb_marketplace_link(
                                vehicle_name,
                                listing['asking_price'],
                                listing.get('city', ''),
                                listing.get('state', '')
                            )
                            st.markdown(f"🔍 [Search on Facebook Marketplace]({fb_search_url})")


def show_deal_finder():
    """Find underpriced deals"""

    st.title("💎 Deal Finder")

    st.markdown("""
    Find vehicles priced significantly below market average.
    These represent the best opportunities for immediate purchase.
    """)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        threshold = st.slider(
            "Minimum Discount (%)",
            min_value=5,
            max_value=25,
            value=10,
            step=5
        )

    with col2:
        price_range = st.slider(
            "Price Range ($)",
            min_value=0,
            max_value=100000,
            value=(5000, 50000),
            step=5000,
            format="$%d"
        )

    with col3:
        max_distance = st.slider(
            "Max Distance (miles)",
            min_value=0,
            max_value=500,
            value=100,
            step=25,
            help="Distance from Santa Cruz / San Jose"
        )

    with col4:
        max_mileage = st.slider(
            "Max Mileage",
            min_value=0,
            max_value=200000,
            value=100000,
            step=10000,
            format="%d mi",
            help="Maximum vehicle mileage"
        )

    deals = repos['market_analyzer'].find_underpriced_listings(threshold_pct=threshold)

    # Filter by price range, mileage, and distance
    if deals:
        # Filter by price range
        deals = [d for d in deals if price_range[0] <= d['asking_price'] <= price_range[1]]

        # Filter by mileage
        deals = [d for d in deals if d['mileage'] <= max_mileage]

        # Filter by distance
        filtered_deals = []
        for deal in deals:
            # Get distance from database
            distance_query = "SELECT distance_miles FROM market_prices WHERE id = ?"
            with repos['db'].get_connection() as conn:
                cursor = conn.execute(distance_query, (deal['listing_id'],))
                result = cursor.fetchone()
                distance = result[0] if result and result[0] is not None else None

            if distance is not None and distance <= max_distance:
                deal['distance'] = distance
                filtered_deals.append(deal)
            elif distance is None and max_distance >= 500:  # Include unknowns if max is high
                deal['distance'] = None
                filtered_deals.append(deal)

        # Sort by distance (closest first)
        filtered_deals.sort(key=lambda x: x['distance'] if x['distance'] is not None else 9999)
        deals = filtered_deals

    if not deals:
        st.info(f"No listings found matching your criteria ({threshold}% discount, ${price_range[0]:,}-${price_range[1]:,}, ≤{max_mileage:,} miles, within {max_distance} mi).")
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
                    location_text = f"**Location:** {deal['location']}"
                    if deal.get('distance') is not None:
                        location_text += f" ({deal['distance']:.0f} miles away)"
                    st.write(location_text)
                    st.write(f"**Condition:** {deal['condition']} | **Mileage:** {deal['mileage']:,}")

                with col2:
                    st.metric("Asking Price", f"${deal['asking_price']:,.0f}")
                    st.metric("Market Average", f"${deal['market_avg']:,.0f}")

                with col3:
                    st.metric("SAVINGS", f"${deal['savings']:,.0f}",
                             delta=f"-{deal['savings_pct']:.1f}%",
                             delta_color="inverse")
                    st.write(f"*Listing ID: {deal['listing_id']}*")

                # Show actual listing URL if available
                # Need to get the listing details to check for source_url
                listing_query = "SELECT source_url FROM market_prices WHERE id = ?"
                with repos['db'].get_connection() as conn:
                    cursor = conn.execute(listing_query, (deal['listing_id'],))
                    listing_row = cursor.fetchone()
                    source_url = listing_row[0] if listing_row else None

                if source_url:
                    st.markdown(f"📍 **Source:** Facebook Marketplace")
                    st.markdown(f"🔗 [View Listing]({source_url})")
                else:
                    location_parts = deal['location'].split(', ')
                    city = location_parts[0] if location_parts else ""
                    state = location_parts[1] if len(location_parts) > 1 else ""
                    fb_search_url = generate_fb_marketplace_link(
                        deal['vehicle'],
                        deal['asking_price'],
                        city,
                        state
                    )
                    st.markdown(f"🔍 [Search on Facebook Marketplace]({fb_search_url})")

                st.markdown("---")


def show_market_analysis():
    """Market analysis and trends"""

    st.title("📊 Market Analysis")

    tab1, tab2, tab3, tab4 = st.tabs(["Regional Pricing", "Best Markets", "Price Trends", "Multi-Dimensional Analysis"])

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

    with tab4:
        st.subheader("Multi-Dimensional Vehicle Analysis")
        st.markdown("Compare vehicles across multiple dimensions: price, mileage, year, MPG, and maintenance costs.")

        # Get unique models for filtering
        query = """
            SELECT DISTINCT v.make, v.model, COUNT(*) as listing_count
            FROM vehicles v
            JOIN market_prices mp ON v.id = mp.vehicle_id
            GROUP BY v.make, v.model
            HAVING listing_count >= 3
            ORDER BY v.make, v.model
        """

        with repos['db'].get_connection() as conn:
            cursor = conn.execute(query)
            models = cursor.fetchall()

        if not models:
            st.warning("Not enough data for analysis. Add more listings.")
        else:
            # Model selector
            model_options = [f"{make} {model} ({count} listings)" for make, model, count in models]
            selected_model = st.selectbox("Select Model to Analyze", model_options)

            if selected_model:
                # Extract make and model from "Tesla Model Y (12 listings)" format
                clean_name = selected_model.split(" (")[0]  # Remove " (12 listings)"
                parts = clean_name.split(maxsplit=1)  # Split on first space only
                make = parts[0]  # "Tesla"
                model = parts[1] if len(parts) > 1 else parts[0]  # "Model Y"

                # Axis selection
                col1, col2 = st.columns(2)

                axis_options = {
                    "Price ($)": "price",
                    "Mileage": "mileage",
                    "Year": "year",
                    "MPG (Est.)": "mpg",
                    "Annual Maintenance Cost (Est.)": "maintenance"
                }

                with col1:
                    x_axis_label = st.selectbox("X-Axis", list(axis_options.keys()), index=1)  # Default: Mileage

                with col2:
                    y_axis_label = st.selectbox("Y-Axis", list(axis_options.keys()), index=0)  # Default: Price

                x_axis = axis_options[x_axis_label]
                y_axis = axis_options[y_axis_label]

                # Optional color dimension
                color_by_label = st.selectbox("Color By (optional)", ["None"] + list(axis_options.keys()), index=3)  # Default: Year
                color_by = axis_options.get(color_by_label, None) if color_by_label != "None" else None

                # Fetch data for selected model
                query = """
                    SELECT
                        v.year,
                        v.make,
                        v.model,
                        mp.asking_price as price,
                        mp.mileage,
                        mp.city,
                        mp.state,
                        mp.distance_miles,
                        mp.source_url,
                        mp.id
                    FROM market_prices mp
                    JOIN vehicles v ON mp.vehicle_id = v.id
                    WHERE v.make = ? AND v.model = ?
                    ORDER BY v.year DESC, mp.asking_price
                """

                with repos['db'].get_connection() as conn:
                    cursor = conn.execute(query, (make, model))
                    listings = cursor.fetchall()

                if not listings:
                    st.warning(f"No listings found for {make} {model}")
                else:
                    # Convert to dataframe
                    df = pd.DataFrame(listings, columns=['year', 'make', 'model', 'price', 'mileage', 'city', 'state', 'distance', 'source_url', 'id'])

                    # Add calculated fields
                    # MPG estimates based on vehicle type and year
                    def estimate_mpg(row):
                        model_lower = row['model'].lower()
                        year = row['year']

                        # Estimates based on common models
                        if 'tacoma' in model_lower:
                            return 21 if year >= 2016 else 19
                        elif '4runner' in model_lower:
                            return 17 if year >= 2010 else 16
                        elif 'highlander' in model_lower:
                            return 24 if year >= 2020 else 21
                        elif 'sequoia' in model_lower:
                            return 15 if year >= 2018 else 14
                        elif 'tundra' in model_lower:
                            return 15 if year >= 2014 else 14
                        elif 'model y' in model_lower or 'model 3' in model_lower:
                            return 120  # MPGe for electric
                        elif 'model s' in model_lower or 'model x' in model_lower:
                            return 105  # MPGe for electric
                        elif 'gx' in model_lower:
                            return 16 if year >= 2014 else 15
                        elif 'lx' in model_lower:
                            return 14 if year >= 2016 else 13
                        elif 'rx' in model_lower:
                            return 25 if year >= 2020 else 22
                        elif 'es' in model_lower:
                            return 28 if year >= 2019 else 25
                        elif 'is' in model_lower:
                            return 26 if year >= 2014 else 24
                        else:
                            return 20  # Default

                    # Maintenance cost estimates (annual, based on age and mileage)
                    def estimate_maintenance(row):
                        age = 2026 - row['year']
                        mileage = row['mileage']

                        # Base cost by brand
                        model_lower = row['model'].lower()
                        if 'tesla' in model_lower or 'model' in model_lower:
                            base = 500  # Electric vehicles
                        elif any(brand in model_lower for brand in ['lexus', 'gx', 'lx', 'rx', 'es', 'is', 'gs']):
                            base = 1000  # Luxury
                        else:
                            base = 800  # Toyota

                        # Age multiplier
                        age_factor = 1 + (age * 0.1)  # 10% increase per year

                        # Mileage factor
                        if mileage > 150000:
                            mileage_factor = 1.5
                        elif mileage > 100000:
                            mileage_factor = 1.3
                        elif mileage > 50000:
                            mileage_factor = 1.1
                        else:
                            mileage_factor = 1.0

                        return int(base * age_factor * mileage_factor)

                    df['mpg'] = df.apply(estimate_mpg, axis=1)
                    df['maintenance'] = df.apply(estimate_maintenance, axis=1)

                    # Create hover text with clickable URL
                    df['hover_text'] = df.apply(
                        lambda row: f"<b>{row['year']} {row['make']} {row['model']}</b><br>" +
                                   f"💰 Price: ${row['price']:,.0f}<br>" +
                                   f"🛣️ Mileage: {row['mileage']:,}<br>" +
                                   f"⛽ MPG: {row['mpg']}<br>" +
                                   f"🔧 Maintenance/yr: ${row['maintenance']:,.0f}<br>" +
                                   f"📍 Location: {row['city']}, {row['state']}" +
                                   (f"<br>📏 Distance: {row['distance']:.0f}mi" if pd.notna(row['distance']) else "") +
                                   (f"<br><br>🔗 <a href='{row['source_url']}' target='_blank' style='color:#1E88E5'>Click to view on Facebook</a>" if pd.notna(row['source_url']) and row['source_url'] else "<br><br>⚠️ No listing URL available"),
                        axis=1
                    )

                    # Calculate linear regression
                    x_data = df[x_axis].values
                    y_data = df[y_axis].values

                    # Remove any NaN values
                    valid_mask = ~(np.isnan(x_data) | np.isnan(y_data))
                    x_clean = x_data[valid_mask]
                    y_clean = y_data[valid_mask]

                    if len(x_clean) >= 3:  # Need at least 3 points for regression
                        # Linear regression
                        slope, intercept, r_value, p_value, std_err = linregress(x_clean, y_clean)
                        r_squared = r_value ** 2

                        # Create prediction line
                        x_range = np.linspace(x_clean.min(), x_clean.max(), 100)
                        y_pred = slope * x_range + intercept

                        # Calculate residuals and standard deviation
                        y_fit = slope * x_clean + intercept
                        residuals = y_clean - y_fit
                        std_residuals = np.std(residuals)

                        # 1 and 2 standard deviation bands
                        y_pred_1std_upper = y_pred + std_residuals
                        y_pred_1std_lower = y_pred - std_residuals
                        y_pred_2std_upper = y_pred + 2 * std_residuals
                        y_pred_2std_lower = y_pred - 2 * std_residuals
                    else:
                        r_squared = None
                        slope = None

                    # Create scatter plot with URLs in customdata
                    if color_by:
                        fig = px.scatter(
                            df,
                            x=x_axis,
                            y=y_axis,
                            color=color_by,
                            hover_data={'hover_text': True, x_axis: False, y_axis: False, color_by: False},
                            custom_data=['source_url'],
                            title=f"{make} {model}: {y_axis_label} vs {x_axis_label}" + (f" (R² = {r_squared:.3f})" if r_squared is not None else ""),
                            labels={x_axis: x_axis_label, y_axis: y_axis_label, color_by: color_by_label},
                            color_continuous_scale='Viridis'
                        )
                    else:
                        fig = px.scatter(
                            df,
                            x=x_axis,
                            y=y_axis,
                            hover_data={'hover_text': True, x_axis: False, y_axis: False},
                            custom_data=['source_url'],
                            title=f"{make} {model}: {y_axis_label} vs {x_axis_label}" + (f" (R² = {r_squared:.3f})" if r_squared is not None else ""),
                            labels={x_axis: x_axis_label, y_axis: y_axis_label}
                        )

                    # Add regression line and confidence bands
                    if len(x_clean) >= 3:
                        # 2 std deviation band (lighter)
                        fig.add_trace(go.Scatter(
                            x=np.concatenate([x_range, x_range[::-1]]),
                            y=np.concatenate([y_pred_2std_upper, y_pred_2std_lower[::-1]]),
                            fill='toself',
                            fillcolor='rgba(128, 128, 128, 0.15)',
                            line=dict(color='rgba(255,255,255,0)'),
                            hoverinfo='skip',
                            showlegend=True,
                            name='±2σ (95% confidence)'
                        ))

                        # 1 std deviation band (darker)
                        fig.add_trace(go.Scatter(
                            x=np.concatenate([x_range, x_range[::-1]]),
                            y=np.concatenate([y_pred_1std_upper, y_pred_1std_lower[::-1]]),
                            fill='toself',
                            fillcolor='rgba(128, 128, 128, 0.25)',
                            line=dict(color='rgba(255,255,255,0)'),
                            hoverinfo='skip',
                            showlegend=True,
                            name='±1σ (68% confidence)'
                        ))

                        # Regression line
                        fig.add_trace(go.Scatter(
                            x=x_range,
                            y=y_pred,
                            mode='lines',
                            line=dict(color='red', width=2, dash='dash'),
                            name=f'Linear Fit (R²={r_squared:.3f})',
                            hovertemplate=f'y = {slope:.2f}x + {intercept:.2f}<extra></extra>'
                        ))

                    # Update hover template for scatter points
                    fig.update_traces(hovertemplate='%{customdata[0]}<extra></extra>', selector=dict(mode='markers'))

                    # Update layout
                    fig.update_layout(
                        height=600,
                        showlegend=True,
                        legend=dict(
                            yanchor="top",
                            y=0.99,
                            xanchor="left",
                            x=0.01
                        )
                    )

                    # Add click event handler to open URLs (client-side, no page reload)
                    st.info("💡 **Click any dot on the chart to open the listing on Facebook Marketplace**")

                    # Generate unique ID for this chart
                    chart_id = f"chart_market_{hash(make + model)}"

                    # Convert figure to HTML with custom click handler
                    plot_html = fig.to_html(include_plotlyjs='cdn', div_id=chart_id)

                    # Add JavaScript to handle clicks
                    custom_html = f"""
                    {plot_html}
                    <script>
                        document.getElementById('{chart_id}').on('plotly_click', function(data) {{
                            var point = data.points[0];
                            if (point.customdata && point.customdata[0]) {{
                                window.open(point.customdata[0], '_blank');
                            }}
                        }});
                    </script>
                    """

                    components.html(custom_html, height=650, scrolling=False)

                    # Regression statistics
                    if len(x_clean) >= 3 and r_squared is not None:
                        st.markdown("---")
                        st.subheader("📈 Regression Analysis")

                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric("R² (Coefficient of Determination)", f"{r_squared:.4f}")
                            quality = "Excellent" if r_squared > 0.8 else "Good" if r_squared > 0.6 else "Moderate" if r_squared > 0.4 else "Weak"
                            st.caption(f"Fit Quality: {quality}")

                        with col2:
                            st.metric("Pearson Correlation (r)", f"{r_value:.4f}")
                            direction = "Strong Positive" if r_value > 0.7 else "Positive" if r_value > 0.3 else "Weak Positive" if r_value > 0 else "Weak Negative" if r_value > -0.3 else "Negative" if r_value > -0.7 else "Strong Negative"
                            st.caption(f"{direction}")

                        with col3:
                            st.metric("Slope", f"{slope:.2f}")
                            st.caption(f"Change in {y_axis_label} per unit {x_axis_label}")

                        with col4:
                            st.metric("Std Deviation (σ)", f"{std_residuals:.2f}")
                            st.caption("Spread around regression line")

                        # Interpretation
                        with st.expander("📊 How to Read This Chart"):
                            st.markdown(f"""
                            **Regression Line (Red Dashed):** Shows the average relationship between {x_axis_label} and {y_axis_label}.

                            **R² = {r_squared:.3f}:** Explains how much of the variation in {y_axis_label} is explained by {x_axis_label}.
                            - R² close to 1.0 = strong relationship
                            - R² close to 0.0 = weak relationship

                            **Standard Deviation Bands:**
                            - **Dark Gray (±1σ):** ~68% of data points fall within this band
                            - **Light Gray (±2σ):** ~95% of data points fall within this band

                            **Points outside 2σ band:** These are outliers - either exceptional deals or overpriced listings.

                            **Slope = {slope:.2f}:** For each 1-unit increase in {x_axis_label}, {y_axis_label} {'increases' if slope > 0 else 'decreases'} by {abs(slope):.2f} on average.
                            """)

                    # Summary statistics
                    st.markdown("---")
                    st.subheader("Summary Statistics")

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Total Listings", len(df))
                        st.metric("Avg Price", f"${df['price'].mean():,.0f}")

                    with col2:
                        st.metric("Price Range", f"${df['price'].min():,.0f} - ${df['price'].max():,.0f}")
                        st.metric("Avg Mileage", f"{df['mileage'].mean():,.0f}")

                    with col3:
                        st.metric("Year Range", f"{df['year'].min()} - {df['year'].max()}")
                        st.metric("Avg MPG", f"{df['mpg'].mean():.1f}")

                    with col4:
                        nearby = df[df['distance'] <= 100].shape[0] if 'distance' in df.columns else 0
                        st.metric("Within 100mi", nearby)
                        st.metric("Avg Maintenance/yr", f"${df['maintenance'].mean():,.0f}")

                    # Clickable listings table
                    st.markdown("---")
                    st.subheader("📋 View All Listings")
                    st.info("💡 **Click the 'View on Facebook' button to open any listing**")

                    # Prepare table data sorted by price
                    table_df = df[['year', 'make', 'model', 'price', 'mileage', 'mpg', 'maintenance', 'city', 'state', 'distance', 'source_url']].copy()
                    table_df = table_df.sort_values('price')

                    # Display listings in expandable rows
                    for idx, row in table_df.iterrows():
                        distance_str = f"{row['distance']:.0f}mi" if pd.notna(row['distance']) else "N/A"
                        with st.expander(f"💰 ${row['price']:,.0f} - {row['year']} {row['make']} {row['model']} @ {row['mileage']:,}mi ({distance_str})"):
                            col_a, col_b, col_c = st.columns([2, 2, 1])
                            with col_a:
                                st.write(f"**Location:** {row['city']}, {row['state']}")
                                if pd.notna(row['distance']):
                                    st.write(f"**Distance:** {distance_str}")
                            with col_b:
                                st.write(f"**MPG:** {row['mpg']}")
                                st.write(f"**Maintenance/yr:** ${row['maintenance']:,.0f}")
                            with col_c:
                                if pd.notna(row['source_url']) and row['source_url']:
                                    st.link_button("🔗 View on Facebook", row['source_url'], use_container_width=True)
                                else:
                                    st.button("⚠️ No URL", disabled=True, use_container_width=True)

                    # Best value finder
                    st.markdown("---")
                    st.subheader("Best Value Analysis")

                    # Calculate value score (lower price, lower mileage, newer, better mpg = higher score)
                    df['value_score'] = (
                        (1 - (df['price'] - df['price'].min()) / (df['price'].max() - df['price'].min() + 1)) * 30 +  # Price 30%
                        (1 - (df['mileage'] - df['mileage'].min()) / (df['mileage'].max() - df['mileage'].min() + 1)) * 25 +  # Mileage 25%
                        ((df['year'] - df['year'].min()) / (df['year'].max() - df['year'].min() + 1)) * 20 +  # Year 20%
                        ((df['mpg'] - df['mpg'].min()) / (df['mpg'].max() - df['mpg'].min() + 1)) * 15 +  # MPG 15%
                        (1 - (df['maintenance'] - df['maintenance'].min()) / (df['maintenance'].max() - df['maintenance'].min() + 1)) * 10  # Maintenance 10%
                    )

                    best_values = df.nlargest(5, 'value_score')[['year', 'make', 'model', 'price', 'mileage', 'mpg', 'maintenance', 'city', 'value_score', 'source_url']]

                    st.markdown("**Top 5 Best Value Vehicles:**")

                    for idx, row in best_values.iterrows():
                        with st.container():
                            col1, col2, col3 = st.columns([2, 2, 1])

                            with col1:
                                st.markdown(f"**{row['year']} {row['make']} {row['model']}**")
                                st.write(f"📍 {row['city']}")

                            with col2:
                                st.write(f"💰 ${row['price']:,.0f} | 🛣️ {row['mileage']:,} mi")
                                st.write(f"⛽ {row['mpg']} MPG | 🔧 ${row['maintenance']:,.0f}/yr")

                            with col3:
                                st.metric("Value Score", f"{row['value_score']:.1f}/100")
                                if pd.notna(row['source_url']) and row['source_url']:
                                    st.markdown(f"[View Listing]({row['source_url']})")

                            st.markdown("---")


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
