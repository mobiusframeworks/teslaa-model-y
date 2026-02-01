#!/usr/bin/env python3
"""
Tesla Model Y Listing Preview
View your listing with photos in browser
"""

import streamlit as st
from pathlib import Path
from PIL import Image
import streamlit.components.v1 as components

# Photo folder - use relative path for deployment
PHOTO_DIR = Path(__file__).parent / "photos"

st.set_page_config(
    page_title="2024 Tesla Model Y - $34,900",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Skip ngrok browser warning
st.markdown("""
    <script>
        window.addEventListener('load', function() {
            if (window.location.hostname.includes('ngrok')) {
                fetch(window.location.href, {
                    headers: {'ngrok-skip-browser-warning': 'true'}
                });
            }
        });
    </script>
""", unsafe_allow_html=True)

# Title
st.title("🚗 2024 Tesla Model Y Long Range AWD - $34,900")
st.markdown("### The Tech Adventurer's Dream Machine")

st.markdown("---")

# Specifications at top
st.markdown("""
### 📊 FULL SPECIFICATIONS

- **Year:** 2024
- **Mileage:** 46,000 miles
- **Drivetrain:** Dual Motor All-Wheel Drive
- **Battery:** Long Range (75 kWh)
- **Horsepower:** 380 HP
- **0-60:** Approximately 4.8 seconds
- **Top Speed:** 135 mph
- **Towing Capacity:** 3,500 lbs
- **Range:** Approximately 300 miles real-world with induction wheels
""")

st.markdown("---")

# Get all photos (excluding last 2)
photos = sorted(list(PHOTO_DIR.glob("IMG_*.jpg")))

if photos:
    st.subheader(f"📸 Photos ({len(photos)} total)")

    # Initialize session state for photo viewing
    if 'viewing_photo' not in st.session_state:
        st.session_state.viewing_photo = None

    # If viewing a specific photo (slideshow mode)
    if st.session_state.viewing_photo is not None:
        idx = st.session_state.viewing_photo

        # Close button at top
        if st.button("✕ Close Slideshow", key="close_top"):
            st.session_state.viewing_photo = None
            st.rerun()

        # Layout: Left arrow | Image | Right arrow
        col1, col2, col3 = st.columns([1, 10, 1])

        with col1:
            st.write("")  # Spacing
            st.write("")
            st.write("")
            if st.button("⬅️", key="prev", use_container_width=True, help="Previous photo"):
                st.session_state.viewing_photo = (idx - 1) % len(photos)
                st.rerun()

        with col2:
            try:
                img = Image.open(photos[idx])
                st.image(img, caption=f"Photo {idx + 1} of {len(photos)}", use_container_width=True)
            except Exception as e:
                st.error(f"Could not load photo")

        with col3:
            st.write("")  # Spacing
            st.write("")
            st.write("")
            if st.button("➡️", key="next", use_container_width=True, help="Next photo"):
                st.session_state.viewing_photo = (idx + 1) % len(photos)
                st.rerun()

    else:
        # Grid view - show all photos
        st.write("Click the image area to view full-size slideshow")

        # Create columns for grid layout
        num_cols = 4
        rows = (len(photos) + num_cols - 1) // num_cols

        for row in range(rows):
            cols = st.columns(num_cols)
            for col_idx in range(num_cols):
                idx = row * num_cols + col_idx
                if idx < len(photos):
                    photo_path = photos[idx]
                    try:
                        img = Image.open(photo_path)
                        img.thumbnail((400, 400))

                        with cols[col_idx]:
                            # Create a container for the image
                            container = st.container()

                            # Show the image
                            container.image(img, use_container_width=True)

                            # Overlay an invisible button that opens slideshow
                            if container.button("🔍 View", key=f"view_{idx}", use_container_width=True):
                                st.session_state.viewing_photo = idx
                                st.rerun()
                    except Exception as e:
                        with cols[col_idx]:
                            st.error(f"Error {idx + 1}")
else:
    st.warning(f"No photos found in: {PHOTO_DIR}")

st.markdown("---")

# Listing content
st.markdown("""
## 2024 Tesla Model Y Long Range AWD - The Tech Adventurer's Dream Machine

For the tech-savvy outdoor enthusiast who wants to teleport to surf breaks, trail heads, and weekend getaways without thinking twice about gas. This isn't just a car - it's your adventure command center on wheels. Bought CPO from Tesla in Jun 2024, fully loaded with every upgrade you need to escape the grid while staying connected.

---

### 🚀 PERFORMANCE & TECHNOLOGY

- **380 HP + Instant Torque** - 0-60 in approximately 4.8 seconds
- **40-120 MPGe equivalent** - Teleport anywhere at pennies per mile (depending on electricity costs)
- **Hardware 4** - Latest FSD-capable computer with AMD Ryzen chip
- **Autopilot up to 85 MPH** - Cuts cognitive load, cruises to and from San Francisco with ease
- **Grok AI Integration** - Real-time web search, research, advice while driving
- **Premium Audio System** - Excellent speakers for road trip playlists
- **Infinitely Customizable** - Every setting adjustable from 15" touchscreen
- **Chill Mode** - Smooth acceleration when you want relaxed driving

---

### 🛡️ TRANSFERABLE WARRANTY (All Coverage Goes to YOU!)

**ALL WARRANTIES TRANSFER AT NO COST** - tied to the VIN, not the owner. This is a HUGE benefit!

- **Basic Vehicle Limited Warranty:** 4,000 miles remaining OR until 2029 (whichever comes first)
- **Battery & Drivetrain Warranty:** Until 120,000 miles OR 2032
- **Used Vehicle Limited Warranty:** 1 year/10,000 miles from Tesla CPO purchase (Jun 2024 @ 33,500 miles)
- **Total remaining coverage:** 74,000 miles OR 6 years of worry-free ownership

**What This Means For You:**
- The original New Vehicle Limited Warranty stays with the car and goes to you until it expires
- The Used Vehicle Limited Warranty that Tesla added when I bought it CPO also transfers to you
- All warranties are tied to the vehicle's VIN - they automatically transfer when you complete the ownership transfer through Tesla
- Zero cost to transfer - just register the vehicle in your Tesla account and the warranty shows up

---

### 🎒 ADVENTURE-READY UPGRADES ($4,000+ in add-ons included)

- **Tesla OEM Roof Rack** - Professionally installed by Tesla
- **Tow Hitch with Connector** - 3,500 lbs towing capacity, ready for bike racks and cargo carriers
- **Induction Wheels (19")** - Aerodynamic design with excellent tire life remaining
- **Mud Flaps** - Front and rear protection installed
- **Premium Window Tint** (professionally done by Mr. Tint, San Jose):
  - XR Plus on front driver/passenger windows
  - Clear windshield tint with glare reduction strip
  - Keeps cabin cool, reduces eye strain on long drives
- **All-Weather Floor Mats** - Front, back, frunk, AND trunk protected
- **Tons of Storage** - Frunk + under-trunk + spacious rear cargo area

---

### 🏕️ CAMPING & ADVENTURE FEATURES

- **Camp Mode** - Built-in Tesla feature: sleep inside with climate control, music, and lights running all night
- **Custom-Fit Inflatable Mattress** - Converts rear seats into full bed (INCLUDED)
- **Blackout Insulated Curtains** - Privacy and temperature control for overnight camping (INCLUDED)
- **Top Glass Reflective Sun Shade** - Windshield protection, keeps interior cool (INCLUDED)
- **Sentry Mode + 256GB USB Storage** - Real-time driver cam monitoring and theft protection
- **Sleep Anywhere** - Park at any Supercharger, run climate control all night, wake up refreshed

---

### 🎨 INTERIOR & EXTERIOR

- **White Vegan Leather Interior** with black seat covers (pristine condition)
- **Solid Black** exterior (classic Tesla look)
- **5-Seat Configuration** - Spacious for adults
- **Panoramic Glass Roof** - UV-protected, incredible views

---

### ⚡ CHARGING & RANGE

- **Approximately 300 miles** real-world range (EPA rated 310 miles with induction wheels)
- **Important Note:** 2024 Model Ys have the same battery as 2023 models, but Tesla adjusted EPA ratings (shows approximately 30 miles less on paper). Actual range is unchanged - this is just updated testing methodology.
- Induction wheels reduce range slightly versus aero wheels but look significantly better
- **Supercharging capable** - 15 minutes = 175 miles of range (250kW peak charging)
- **Charge at home** overnight on any outlet (Level 1 or Level 2)
- **40-120 MPGe equivalent** - costs pennies compared to gasoline

---

### 💎 WHY THIS ONE OVER OTHERS?

1. **Tech Meets Adventure** - Not just a car, it's your adventure command center
2. **Camp Mode Ready** - Sleep anywhere: beach, mountains, Supercharger parking lots
3. **Autopilot to 85 MPH** - Makes long drives to surf/ski/trail completely effortless
4. **Low Operating Costs** - $150/month insurance, $30-50 charging versus $200+ for gas
5. **Teleport Economics** - 40-120 MPGe equivalent means go anywhere without worrying about fuel costs
6. **Hardware 4 Future-Proof** - Latest technology, over-the-air updates, FSD-capable
7. **Complete Adventure Package** - Roof rack, tow hitch, camping gear, all-weather mats all included
8. **Sentry Mode Protection** - 256GB storage, real-time monitoring, excellent theft deterrent
9. **CPO Warranty Coverage** - 74,000 miles OR 6 years of worry-free ownership remaining
10. **$4,000+ in Upgrades** - All included at no additional cost
11. **No Dealer Markup** - Private sale, clean title, completely transparent
12. **Optional Bike Rack Available** - Add Inno 2-bike rack for just $300

---

### 🔧 MAINTENANCE HISTORY

- Serviced by Tesla (CPO inspection completed June 2025)
- **Clean Title** - No accidents
- **Non-Smoker** - Pristine interior condition
- **Garage Kept** when at home

---

### 💡 FULL SELF-DRIVING UPGRADE (Optional)

This car is FSD-capable with Hardware 4 (latest generation). You can add Full Self-Driving capability anytime:

- **$99/month subscription** (cancel anytime)
- **$8,000 one-time purchase**

Features include: Navigate on Autopilot, Auto Lane Change, Autopark, Summon, Traffic Light and Stop Sign Control, and more future features as they're released.

---

### 📍 LOCATION

**Santa Cruz / San Jose, California** (Bay Area)
- Easy freeway access
- Can meet at Tesla Supercharger for test drives
- Happy to demonstrate all features

---

### 📞 CONTACT & TEST DRIVE

Serious buyers only - no lowballers please. Clean title in hand, ready for immediate sale.

**Price:** $34,900 OBO
**Available:** Immediately
**Test Drives:** By appointment (meet at public location)

Please message me with:
1. Your name
2. Your availability for test drive
3. Financing confirmation (if applicable)

---

### 🎁 WHAT'S INCLUDED

- All keys and key cards
- **Tesla Mobile Charger with extension cable**
- Original Tesla accessories
- Roof rack crossbars
- Tow hitch hardware
- All-weather floor mats (front, back, frunk, trunk)
- Black seat covers
- Mud flaps (front and rear)
- **Work desk for laptop use in vehicle**
- Inflatable camping mattress (custom-fit)
- Blackout insulated curtains (privacy and temperature control)
- Top glass reflective sun shade
- 256GB USB drive for dashcam/Sentry Mode
- Owner's manual and documentation

---

### 🎯 OPTIONAL ADD-ON

**Inno 2-bike hitch rack:** Additional $300 (retail value $400+)

---

**First come, first served. Adventure awaits!**

**- Alex, Santa Cruz**

---

### 📞 CONTACT INFORMATION

**Preferred Contact Method:** Facebook Marketplace Messaging (keeps your info private!)

**Alternative Contact:**
- **Phone/Text:** (831) 316-4073
- **Email:** teslamodelyawd2024sc@gmail.com

**Test Drive Requirements:**
- Valid driver's license
- By appointment only

---

**💬 Contact Alex:**

📱 **(831) 316-4073**

📧 **teslamodelyawd2024sc@gmail.com**

**- Alex, Santa Cruz**

---
""")

st.markdown("---")
st.success(f"✓ {len(photos)} photos loaded")
