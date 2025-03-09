import streamlit as st
import requests
import geocoder
import pandas as pd

API_KEY = ""

def get_user_location():
    g = geocoder.ip("me")  
    if g.ok:
        return g.latlng
    return None

def search_electronic_stores(latitude, longitude, zoom=30):
    params = {
        "api_key": API_KEY,
        "engine": "google_maps",
        "type": "search",
        "q": "electronic stores",
        "ll": f"@{latitude},{longitude},{zoom}z",
        "hl": "en",
        "gl": "us"
    }
    
    response = requests.get("https://serpapi.com/search.json", params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("local_results", [])
    return None

st.set_page_config(page_title="Electronic Store Finder", layout="centered")

st.markdown("""
    <style>
        .green-text {
            color: green !important;
            font-weight: bold;
        }
        .small-font {
            font-size: 14px !important;
            color: white !important;
        }
        .dataframe td, .dataframe th {
            font-size: 12px !important;
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='green-text'>🔌 Nearby Electronic Stores Finder</h1>", unsafe_allow_html=True)
st.write("Find electronic stores near you using SerpAPI and Google Maps.")

location = get_user_location()

if location:
    lat, lon = location
    st.markdown(f"✅ Your location detected: <b>Lat:</b> {lat}, <b>Lon:</b> {lon}")
    
    # Search for stores
    with st.spinner("Searching for electronic stores..."):
        stores = search_electronic_stores(lat, lon)

    if stores:
        st.markdown("<h2 class='green-text'>📍 Electronic Stores Near You:</h2>", unsafe_allow_html=True)

        data = []
        for shop in stores:
            name = shop.get("title", "Unknown Store")
            address = shop.get("address", "No address available")
            website = shop.get("website", "#")
            website_link = f"[Visit]({website})" if website != "#" else "N/A"
            data.append([name, address, website_link])

        df = pd.DataFrame(data, columns=["Store Name", "Address", "Website"])

        st.dataframe(df, use_container_width=True)
    else:
        st.markdown("⚠️ No electronic stores found nearby.")
else:
    st.markdown("❌ Could not detect your location. Please enable location services.")
