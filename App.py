import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import math

st.set_page_config(page_title="SAR POD Planner", layout="wide")

st.title("🗺️ SAR Search Area & POD Calculator")
st.sidebar.header("Asset Parameters")

# Sidebar Inputs
asset_type = st.sidebar.selectbox("Asset Type", ["Foot Team", "Drone", "Helicopter", "K9"])
sweep_width = st.sidebar.slider("Sweep Width (meters)", 5, 500, 50)
search_speed = st.sidebar.slider("Search Speed (km/h)", 1.0, 60.0, 3.0)
target_pod = st.sidebar.slider("Target POD (%)", 50, 99, 80)

st.info("Instructions: Use the Polygon tool on the left of the map to draw your search area.")

# Initialize Map
m = folium.Map(location=[-37.8136, 144.9631], zoom_start=13) # Default view
# Add drawing tools
draw_options = {'polyline': False, 'rectangle': True, 'polygon': True, 'circle': False, 'marker': False}
folium.plugins.Draw(export=True, draw_options=draw_options).add_to(m)

# Display Map and capture user drawing
output = st_folium(m, width=900, height=500)

# Calculation Logic
if output['all_drawings']:
    # Get the coordinates of the last drawn shape
    last_draw = output['all_drawings'][-1]
    coords = last_draw['geometry']['coordinates'][0]
    
    # Calculate Area using Shapely (Approximation in square meters)
    # Note: For real-world use, use a library like pyproj for accurate geodesic area
    poly = Polygon(coords)
    # Rough conversion from lat/long degrees to meters (approx for mid-latitudes)
    area_m2 = poly.area * 111139 * 111139 * math.cos(math.radians(coords[0][1]))
    area_km2 = area_m2 / 1_000_000

    st.success(f"### Results for Area: {area_km2:.2f} km²")

    # 1. Calculate Required Effort for Target POD
    # Formula: POD = 1 - e^(-Coverage) -> Coverage = -ln(1 - POD)
    required_coverage = -math.log(1 - (target_pod / 100))
    
    # 2. Total Track Length Needed (km)
    # Coverage = (Distance * SweepWidth) / Area
    total_distance_km = (required_coverage * area_m2) / sweep_width / 1000

    # 3. Time Required (Hours)
    total_time_hours = total_distance_km / search_speed

    # UI Display
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Track Length", f"{total_distance_km:.2f} km")
    with col2:
        st.metric("Required Effort", f"{total_time_hours:.1f} Hours")
    with col3:
        st.metric("Spacing (Track Spacing)", f"{sweep_width} m")

    st.write(f"**Recommendation:** To achieve a **{target_pod}% POD**, you need **{math.ceil(total_time_hours/4)} teams** working for 4 hours each.")
else:
    st.write("Draw an area on the map to begin calculations.")
