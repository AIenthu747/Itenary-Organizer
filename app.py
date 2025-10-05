import streamlit as st
import os
import re
from dotenv import load_dotenv
from openai import OpenAI
import requests

load_dotenv()

# --- Configure OpenRouter API ---
try:
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_api_key:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_api_key,
        )
    else:
        st.error("OpenRouter API key not found in environment variables. "
                 "Please set OPENROUTER_API_KEY in your .env file locally.")
        st.stop()
except Exception as e:
    st.error(f"Error configuring OpenRouter API: {e}")
    st.stop()


# --- Function to get a suitable model from OpenRouter (Revised prioritization) ---
# --- Function to get a suitable model from OpenRouter (Revised prioritization) ---
# --- Function to get a suitable model from OpenRouter (Revised prioritization and AGGRESSIVE DEBUGGING) ---
@st.cache_data(ttl=3600, show_spinner="Attempting to find a robust OpenRouter model...")
def get_suitable_openrouter_model():
    """
    F etches available models from OpenRouter and selects a robust text generation one.
    Prioritizes commonly used, reliable chat models.
    """
    try:
        headers = {"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"} # Ensure API key is correctly accessed
        
        st.info("Making API call to OpenRouter to list models...")
        response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
        response.raise_for_status() 
        
        models_data = response.json().get('data', [])
        
        if not models_data:
            st.error("OpenRouter API returned an EMPTY list of models. This is highly unusual and suggests an issue with your API key or account.")
            st.error("Please re-check your OpenRouter API key on your account dashboard and ensure you have sufficient credits/plan for any model to be listed.")
            return None
        
        st.info(f"OpenRouter API returned {len(models_data)} raw models. (First 3 IDs: {[m.get('id') for m in models_data[:3]]})")

        preferred_models_ids = [
            "mistralai/mixtral-8x7b-instruct",
            "openai/gpt-3.5-turbo",
            "openai/gpt-4-turbo", 
            "google/gemini-pro", 
            "anthropic/claude-3-opus", 
            "anthropic/claude-3-sonnet", 
            "anthropic/claude-instant-v1",
            "mistralai/mistral-7b-instruct",
            "nousresearch/nous-hermes-2-mixtral-8x7b-dpo",
            "meta-llama/llama-2-70b-chat", 
            "databricks/dbrx-instruct",
            "anthropic/claude-sonnet-4.5", # Explicitly adding one from your debug output
            "google/gemini-2.5-flash-preview-09-2025" # Another from your output that looks promising
        ]

        selected_model_id = None
        available_chat_models = []
        
        st.write("--- Attempting to filter models for chat capabilities (detailed log) ---")
        
        debug_log_limit = 20 
        logged_models_count = 0

        for model_config in models_data:
            model_id = model_config.get('id')
            architecture_config = model_config.get('architecture', {})
            modality = architecture_config.get('modality')
            context_length = model_config.get('context_length')

            is_suitable = True
            reasons_for_filter = []

            # Check 1: Model ID must exist
            if not model_id:
                is_suitable = False
                reasons_for_filter.append("Missing ID")
            
            # Check 2: Modality must indicate text output
            # REVISED: Check if modality starts with 'text' or contains '->text'
            if modality is None: # Modality might be missing for some models
                is_suitable = False
                reasons_for_filter.append("Modality is missing (None)")
            elif not (modality.startswith('text') or '->text' in modality):
                is_suitable = False
                reasons_for_filter.append(f"Modality '{modality}' does not indicate text output")

            # Check 3: Context length should exist and be reasonable
            if not context_length or not isinstance(context_length, int) or context_length < 500: # Assuming minimal context for a chat model
                is_suitable = False
                reasons_for_filter.append(f"Invalid or missing context_length ({context_length})")

            # Check 4: Keywords indicating chat/instruction capability
            model_id_lower = model_id.lower() if model_id else ""
            if not any(keyword in model_id_lower for keyword in 
                       ['chat', 'instruct', 'gpt', 'claude', 'gemini', 'llama', 'mistral', 'hermes', 'dpo', 
                        'text-generation', 'command', 'qwen', 'mixtral', 'openhermes', 'codellama', 'glm', 'grok', 'deepseek']):
                is_suitable = False
                reasons_for_filter.append(f"No chat/instruct keyword found in ID '{model_id}'")

            if is_suitable:
                available_chat_models.append(model_id)
                if logged_models_count < debug_log_limit:
                    st.write(f"✅ SUITABLE: `{model_id}` (Modality: {modality}, Context: {context_length})")
                    logged_models_count += 1
            else:
                if logged_models_count < debug_log_limit:
                    st.write(f"❌ FILTERED: `{model_id}` (Modality: {modality}, Context: {context_length}) - Reasons: {'; '.join(reasons_for_filter)}")
                    logged_models_count += 1


        if not available_chat_models:
            st.error("Even after extensive filtering, no suitable chat/instruction-following text models were found for your API key.")
            st.error("This suggests models might be unavailable or your filtering criteria are too strict for your account's access.")
            return None

        available_chat_models.sort() 

        for preferred_id in preferred_models_ids:
            if preferred_id in available_chat_models:
                selected_model_id = preferred_id
                break
        
        if not selected_model_id:
            selected_model_id = available_chat_models[0] 
            st.warning(f"No highly preferred model found among available chat models. Using first available: `{selected_model_id}`")

        st.success(f"Successfully selected OpenRouter model: `{selected_model_id}`.")
        return selected_model_id

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            st.error(f"OpenRouter API Key Unauthorized (401). Your OPENROUTER_API_KEY is likely incorrect or expired. Error: {e}")
            st.error("Please go to your OpenRouter account, generate a NEW API KEY, and update your .env file.")
        else:
            st.error(f"Failed to fetch models from OpenRouter due to HTTP error {e.response.status_code}: {e}")
            st.error(f"OpenRouter's response: {e.response.text}") 
        return None
    except requests.exceptions.ConnectionError as e:
        st.error(f"Failed to connect to OpenRouter. Check your internet connection or firewall. Error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"An unknown request error occurred while fetching models from OpenRouter: {e}")
        st.error("This usually means a problem with the API key or network.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while selecting an OpenRouter model: {e}")
        st.error("This could be due to unexpected data format from OpenRouter or other Python errors.")
        return None

    
# --- get_openrouter_response() function (WITH AGGRESSIVE DEBUGGING) ---
def get_openrouter_response(prompt_text):
    """Sends a prompt to OpenRouter and returns the text response."""
    
    debug_status = st.empty() 
    
    openrouter_client = client 
    debug_status.info("DEBUG: Inside get_openrouter_response(). Attempting to get model ID.")

    model_id = get_suitable_openrouter_model()
    if not model_id:
        debug_status.error("DEBUG: Model ID could NOT be retrieved. Returning None.")
        return None 
    
    debug_status.info(f"DEBUG: Model ID successfully retrieved: `{model_id}`. Preparing API call.")

    if not prompt_text or not prompt_text.strip():
        debug_status.error("DEBUG: Prompt text is empty or only whitespace. Cannot send empty prompt to LLM.")
        return None

    try:
        debug_status.info(f"DEBUG: Sending chat completion request to OpenRouter with model `{model_id}`...")
        response = openrouter_client.chat.completions.create(
            model=model_id, 
            messages=[
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.7, 
            max_tokens=1500, 
        )
        debug_status.info("DEBUG: Chat completion request successful. Extracting content.")
        
        if response and response.choices and len(response.choices) > 0 and response.choices[0].message and response.choices[0].message.content is not None:
            # Explicitly check for 'is not None' because an empty string '' is valid content
            final_content = response.choices[0].message.content
            if not final_content.strip(): # Check if content is just whitespace
                debug_status.warning(f"DEBUG: Model `{model_id}` returned content, but it was empty or only whitespace. This may indicate a problem with the prompt or the model's ability to respond.")
                st.write("Full OpenRouter response object:")
                st.json(response.model_dump_json())
            else:
                debug_status.success("DEBUG: Successfully extracted non-empty content from OpenRouter response.")
            return final_content
        else:
            debug_status.error("DEBUG: OpenRouter response was malformed or did not contain expected message content.")
            st.write("Full OpenRouter response object:")
            st.json(response.model_dump_json()) 
            return None

    except Exception as e:
        debug_status.error(f"DEBUG: An EXCEPTION occurred during OpenRouter API call with model '{model_id}': {e}")
        import traceback
        st.exception(e) 
        debug_status.error("DEBUG: Check the console/Streamlit for detailed traceback above.")
        return None


# --- Main Itinerary Organization Function (uses OpenRouter now) ---
# --- Main Itinerary Organization Function (uses OpenRouter now) ---
def organize_itinerary_with_openrouter(raw_itinerary_components, num_days_str="3N 4D"):
    """
    Leverages OpenRouter (using a specified model) to organize raw itinerary components
    into a structured, day-by-day format with desired beautification and constraints.
    """

    prompt = f"""
    You are an expert travel agent assistant. Your task is to take raw itinerary components and organize them into a structured, day-by-day plan.

    Here are the raw itinerary components:
    {raw_itinerary_components}

    The trip duration is {num_days_str}.

    Please format the output *strictly* as follows for easy copy-pasting:
    - Each day starts with: 🗓️Day "n" : One liner brief of the day
    - Each activity point starts with: → (use the arrow symbol, not bullet points)
    - **CRITICAL:** Each activity point MUST be on its own separate line. Absolutely no two points should share the same line.
    - Each day (except departure day if it has minimal activities) must have a minimum of 3 to 4 clearly detailed and catchy points.
    - After significant tours or activities, **always add a point like "→ Transfer back to your hotel for relaxation."** or similar, ensuring a complete daily flow.
    - EXCEPTION: For days that are primarily "Departure" days with no significant activities other than transfer, limit the points to a maximum of 2, ensuring they are concise and brief.

    Here is an example of the desired format for a day (ensure you follow the "→" arrow strictly, and note each point is on a new line):
    🗓️Day 1 : Arrival & Enchanting City Discoveries
    → Arrive in Singapore and enjoy a seamless private transfer to your hotel.
    → Embark on a comprehensive 3-hour City Tour, uncovering Singapore's vibrant heart.
    → Capture stunning photos at iconic landmarks like the majestic Singapore Flyer.
    → Drive past architectural gems including Raffles Hotel and the poignant War Memorial Park.
    → Conclude your city insights with a visit to a charming Gift Shop and explore Chinatown.
    → Transfer back to your hotel for relaxation after a day of exploration.

    Please ensure all the provided tours and transfers are incorporated logically into the {num_days_str} duration.
    Focus on creating engaging and appealing descriptions for each point.
    Do not include any introductory or concluding remarks outside the formatted itinerary. Just output the itinerary.
    """
    
    st.expander("Show Generated Prompt").code(prompt)

    with st.spinner("Crafting your perfect itinerary using OpenRouter..."):
        openrouter_output = get_openrouter_response(prompt)

    if openrouter_output:
        st.success("DEBUG: OpenRouter successfully returned output. Attempting regex match.")
        match = re.search(r'🗓️Day 1 :.*', openrouter_output, re.DOTALL)
        if match:
            cleaned_output = match.group(0)
            st.success("DEBUG: Regex match found.")
            return cleaned_output
        else:
            st.warning("DEBUG: Regex match NOT found for '🗓️Day 1 :'. Displaying full output.")
            st.markdown("--- Full raw OpenRouter output (no regex match) ---")
            st.markdown(openrouter_output)
            st.markdown("--- End raw output ---")
            return openrouter_output 
    else:
        st.error("DEBUG: get_openrouter_response() returned None. Itinerary could not be generated.")
        return "Could not generate itinerary. Please try again."


# --- Streamlit UI Layout (remains the same from here down) ---
st.set_page_config(
    page_title="AI-Powered Itinerary Organizer",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ AI-Powered Itinerary Organizer (via OpenRouter)")
st.markdown("""
    Welcome to your personal itinerary assistant!
    Paste your raw trip details below, and I'll transform them into a beautifully organized, day-by-day plan
    following your desired format, powered by OpenRouter.
""")

st.subheader("Trip Duration")
duration_options = ["2N 3D", "3N 4D", "4N 5D", "5N 6D", "6N 7D", "7N 8D", "Custom"]
selected_duration = st.selectbox(
    "Select the duration of your trip:",
    duration_options,
    index=1
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

if st.button("Organize Itinerary", type="primary"):
    if raw_itinerary_text.strip():
        organized_itinerary = organize_itinerary_with_openrouter(raw_itinerary_text, num_days_str=duration_to_use)
        st.subheader("✨ Your Organized Itinerary:")
        st.markdown(organized_itinerary)
    else:
        st.warning("Please enter some raw itinerary details to get started!")

st.markdown("---")
st.info("Powered by OpenRouter and Streamlit.")