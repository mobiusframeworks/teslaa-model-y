# 🚗 Car Valuation Dashboard

Interactive market analysis dashboard for vehicle pricing with clickable charts and regression analysis.

## 📊 Features

- **Interactive Regression Analysis**: Linear regression with ±1σ and ±2σ confidence bands
- **Clickable Data Points**: Click any dot on the chart to open Facebook Marketplace listing
- **Real-time Market Data**: 339 vehicle listings with 100% URL coverage
- **Distance Filtering**: Filter listings by distance from Santa Cruz/San Jose
- **Multi-dimensional Analysis**: Compare price vs mileage, year, MPG, and more
- **Mobile Responsive**: Works on desktop, tablet, and mobile devices

## 🎯 Live Demo

Visit the live dashboard: [Car Optimization Dashboard](https://your-app.streamlit.app)

## 📱 Usage

1. Select a vehicle model from the dropdown
2. Choose your analysis axes (X: Mileage, Y: Price, Color: Year)
3. View regression statistics and R² correlation scores
4. **Click any dot** on the chart to open the listing on Facebook Marketplace
5. Browse expandable listing cards below the chart

## 🗄️ Database

- **339 total listings** from Facebook Marketplace and Google Shopping
- **100% URL coverage** - every listing is clickable
- **Vehicles included**: Toyota (Tacoma, 4Runner, Highlander, Sequoia, Tundra), Lexus (GX, RX, LX, ES), Tesla
- **67.8% distance data** for location-based filtering

## 🚀 Deployment

This app is deployed on Streamlit Cloud for free public hosting.

### Local Development

```bash
git clone <your-repo-url>
cd car-optimization
pip install -r requirements.txt
streamlit run dashboard.py
```

## 📈 Analysis Features

- **Linear Regression**: Statistical trend analysis
- **Confidence Bands**: ±1σ (68%) and ±2σ (95%) probability ranges  
- **R² Correlation**: Measure relationship strength between variables
- **Outlier Detection**: Identify deals outside 2σ bands
- **Best Value Analysis**: Automated value scoring based on price, mileage, year, MPG

## 🛠️ Tech Stack

- **Frontend**: Streamlit 1.53.1
- **Charts**: Plotly 6.5.2 with custom JavaScript click handlers
- **Data**: Pandas 2.3.3, NumPy 2.4.1
- **Statistics**: SciPy 1.17.0 for regression analysis
- **Database**: SQLite3 (built-in)

## 📊 Data Sources

- Facebook Marketplace scrapes (320 listings)
- Google Shopping results (19 listings)
- All listings verified with clickable URLs

## 🎨 Features in Detail

### Clickable Charts
Click any data point to instantly open the vehicle listing in a new tab - no page reload required.

### Regression Analysis
View statistical trends with:
- Red dashed line: Linear regression fit
- Dark gray band: ±1σ (68% of data)
- Light gray band: ±2σ (95% of data)
- R² score: Correlation strength

### Distance Filtering
Filter listings by proximity to Santa Cruz/San Jose area (0-500 miles).

## 📄 License

MIT License - feel free to use and modify.

## 👤 Author

Built with Claude Sonnet 4.5
