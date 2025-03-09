import streamlit as st
import requests
import geocoder
import pandas as pd

# FastAPI endpoint
API_URL = "http://127.0.0.1:8000/caption_image"
# SerpAPI key
API_KEY = "ae0444450b674e53904e754317ba48ec4f5ce650fdcb0ca1a0fe20a1d36f3948"

# Initialize session state for storing results
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

# Set page config
st.set_page_config(page_title="E-Wise", layout="wide")

# Custom CSS
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
        .stApp {
            max-width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# Main title
st.title("E-Wise - Electronic Device Solutions")

# Create two columns for the 50/50 split
col1, col2 = st.columns(2)

# Function to send the image to FastAPI
def process_image(uploaded_file):
    files = {"file": uploaded_file.getvalue()}
    response = requests.post(API_URL, files=files)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to display results
def display_results(response):
    st.subheader("Analysis Results")
    
    st.write(f"**Device Type:** {response.get('captions', ['Unknown Device'])[0]}")
    st.write(f"**Damaged Component:** {response.get('qa_responses', [{'answers': ['Unknown Component']}])[1]['answers'][0]}")
    st.write(f"**Description:** {response.get('gemini_responses', [{'answers': ['No description available']}])[1]['answers']}")

    st.subheader("Repair Steps")
    repair_steps = response.get("advice", "No repair steps available.").split(". ")
    for step in repair_steps:
        st.write(f"- {step}")

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

# Left column - Image Analysis
with col1:
    st.header("Image Analysis")
    st.write("Upload an image of an electronic device to identify damaged components and get repair suggestions.")
    
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

        # Button to analyze image
        if st.button("Analyze Image"):
            with st.spinner("Analyzing image..."):
                response = process_image(uploaded_file)
                if response:
                    st.session_state.analysis_results = response
                else:
                    st.error("Failed to analyze image. Please try again.")

    # Display results if they exist
    if st.session_state.analysis_results:
        with st.container():
            display_results(st.session_state.analysis_results)

# Right column - Store Finder
with col2:
    st.header("🔌 Nearby Electronic Stores Finder")
    st.write("Find electronic stores near you for repairs or purchases.")
    
    location = get_user_location()

    if location:
        lat, lon = location
        st.markdown(f"✅ Your location detected: <b>Lat:</b> {lat}, <b>Lon:</b> {lon}", unsafe_allow_html=True)
        
        # Search for stores
        with st.spinner("Searching for electronic stores..."):
            stores = search_electronic_stores(lat, lon)

        if stores:
            st.markdown("<h3 class='green-text'>📍 Electronic Stores Near You:</h3>", unsafe_allow_html=True)

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

url = "http://127.0.0.1:5500/main/parts.html"
st.subheader("Parts finder")
st.write("check out this [link](%s)" % url)