import streamlit as st
import google.generativeai as genai
import os
import re
from dotenv import load_dotenv

load_dotenv()

# --- Configure Gemini API ---
# Streamlit provides a secure way to handle secrets: st.secrets
try:
    # if "GOOGLE_API_KEY" in st.secrets:
    #     genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # else:
    #     st.error("Gemini API key not found in Streamlit secrets. "
    #              "Please add it to .streamlit/secrets.toml (GOOGLE_API_KEY=\"YOUR_API_KEY\")")
    #     st.stop() # Stop the app if API key is not available
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if google_api_key:
        genai.configure(api_key=google_api_key)
    else:
        st.error("Gemini API key not found in environment variables. "
                 "Please set GOOGLE_API_KEY in your .env file.")
        st.stop() # Stop the app if API key is not available
except Exception as e:
    st.error(f"Error configuring Gemini API: {e}")
    st.stop()


@st.cache_data(show_spinner=False) # Cache the model to avoid re-loading on every rerun
def get_gemini_model():
    """Loads and returns the Gemini Pro generative model."""
    return genai.GenerativeModel('gemini-pro')

# --- Function to interact with Gemini ---
def get_gemini_response(prompt_text):
    """Sends a prompt to the Gemini API and returns the text response."""
    model = get_gemini_model()
    try:
        response = model.generate_content(prompt_text)
        return response.text
    except Exception as e:
        st.error(f"Error calling Gemini API: {e}")
        return None

# --- Main Itinerary Organization Function ---
def organize_itinerary_with_gemini(raw_itinerary_components, num_days_str="3N 4D"):
    """
    Leverages Gemini API to organize raw itinerary components into a structured,
    day-by-day format with desired beautification and constraints.
    """

    prompt = f"""
    You are an expert travel agent assistant. Your task is to take raw itinerary components and organize them into a day-by-day plan.

    Here are the raw itinerary components:
    {raw_itinerary_components}

    The trip duration is {num_days_str}.

    Please format the output exactly as follows:
    - Each day starts with: 🗓️Day "n" : One liner brief of the day
    - Each activity point starts with: → (use the arrow symbol, not bullet points)
    - Each day must have a minimum of 4 to 5 points, clearly detailed and catchy.
    - EXCEPTION: For days that are primarily "Departure" days with no significant activities other than transfer, limit the points to a maximum of 2, ensuring they are concise and brief.

    Here is an example of the desired format for a day (ensure you follow the "→" arrow strictly):
    🗓️Day 1 : Arrival & Enchanting City Discoveries
    → Arrive in Singapore and enjoy a seamless private transfer to your hotel.
    → Embark on a comprehensive 3-hour City Tour, uncovering Singapore's vibrant heart.
    → Capture stunning photos at iconic landmarks like the majestic Singapore Flyer.
    → Drive past architectural gems including Raffles Hotel and the poignant War Memorial Park.
    → Conclude your city insights with a visit to a charming Gift Shop and explore Chinatown.

    Please ensure all the provided tours and transfers are incorporated logically into the {num_days_str} duration.
    Focus on creating engaging and appealing descriptions for each point.
    Do not include any introductory or concluding remarks outside the formatted itinerary. Just output the itinerary.
    """

    with st.spinner("Crafting your perfect itinerary..."):
        gemini_output = get_gemini_response(prompt)

    if gemini_output:
        # Gemini is usually good at following "Just output the itinerary" but we add a regex cleanup just in case.
        match = re.search(r'🗓️Day 1 :.*', gemini_output, re.DOTALL)
        if match:
            cleaned_output = match.group(0)
            return cleaned_output
        return gemini_output # Fallback if regex doesn't match
    else:
        return "Could not generate itinerary. Please try again."

# --- Streamlit UI Layout ---
st.set_page_config(
    page_title="AI-Powered Itinerary Organizer",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ AI-Powered Itinerary Organizer")
st.markdown("""
    Welcome to your personal itinerary assistant!
    Paste your raw trip details below, and I'll transform them into a beautifully organized, day-by-day plan
    following your desired format.
""")

# Input for Trip Duration
st.subheader("Trip Duration")
duration_options = ["2N 3D", "3N 4D", "4N 5D", "5N 6D", "6N 7D", "7N 8D", "Custom"]
selected_duration = st.selectbox(
    "Select the duration of your trip:",
    duration_options,
    index=1 # Default to "3N 4D"
)

custom_duration = ""
if selected_duration == "Custom":
    custom_duration = st.text_input(
        "Enter custom duration (e.g., '10N 11D', '5 days'):",
        "3N 4D"
    )
    duration_to_use = custom_duration
else:
    duration_to_use = selected_duration


# Input for Raw Itinerary Text
st.subheader("Raw Itinerary Details")
raw_input_example = """
Tours:
- City Tour (3hrs) ** SIC Basis  ** (Singapore Flyer and Merlion [2 Photostops], Drive Past: Raffles Hotel, Swiss Hotel, War Memorial Park, Suntec City, Supreme Court, Gift Shop, and Chinatown, ending at Little India.)
- Singapore River Cruise ** PVT Basis  **
- Gardens by the Bay: Flower Dome + Cloud Forest [Jurassic World: The Exhibition} (29 May 2025 - 31 March 2026) ** SIC Basis  **
- Night Safari (Admission + Tram)(01 Oct 25 Onwards) ** SIC Basis  **

Transfers:
 - (1) Arrival / (1) Departure Transfers (Private basis)
 - (5) Tour Transfer - City Tour (3hrs), Gardens by the Bay: Flower Dome + Cloud Forest [Jurassic World: The Exhibition} (29 May 2025 - 31 March 2026), Night Safari (Admission + Tram)(01 Oct 25 Onwards) (Seat in Coach basis)
 - (2) Tour Transfers  - Singapore River Cruise (Private basis)
"""

raw_itinerary_text = st.text_area(
    "Paste your unorganized itinerary components here:",
    raw_input_example,
    height=300
)

# Button to trigger generation
if st.button("Organize Itinerary", type="primary"):
    if raw_itinerary_text.strip():
        organized_itinerary = organize_itinerary_with_gemini(raw_itinerary_text, num_days_str=duration_to_use)
        st.subheader("✨ Your Organized Itinerary:")
        st.markdown(organized_itinerary)
    else:
        st.warning("Please enter some raw itinerary details to get started!")

st.markdown("---")
st.info("Powered by Google Gemini API and Streamlit.")