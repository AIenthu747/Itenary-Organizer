# ✈️ AI-Powered Itinerary Organizer

## Description
This Streamlit application helps you organize raw travel itinerary components into a structured, day-by-day plan using the power of large language models (LLMs) via the OpenRouter API. Simply paste your trip details, select the duration, and let the AI craft a beautifully organized itinerary for you.

## Features
- **Intelligent Itinerary Generation**: Leverages advanced LLMs to transform unstructured trip details into a coherent daily plan.
- **Customizable Duration**: Choose from predefined trip durations or specify a custom number of days and nights.
- **Structured Output**: Generates itineraries with a clear, easy-to-read format, including daily briefs and activity points.
- **OpenRouter Integration**: Utilizes OpenRouter to access a variety of LLMs, providing flexibility and potentially better model performance.
- **User-Friendly Interface**: Built with Streamlit for a simple and intuitive web interface.

## Installation

### Prerequisites
- Python 3.8+

### Steps
1.  **Clone the repository (if applicable):**
    ```bash
    git clone <repository_url>
    cd Itenary-Organizer
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ./venv/Scripts/activate  # On Windows
    source venv/bin/activate # On macOS/Linux
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up OpenRouter API Key:**
    - Create an account and obtain an API key from [OpenRouter](https://openrouter.ai/).
    - Create a `.env` file in the root directory of the project (same level as `app.py`).
    - Add your OpenRouter API key to the `.env` file:
      ```
      OPENROUTER_API_KEY="your_openrouter_api_key_here"
      ```
      (Replace `your_openrouter_api_key_here` with your actual key.)

## Usage

1.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```

2.  **Open in browser**: The application will open in your web browser (usually `http://localhost:8501`).

3.  **Enter Details**: 
    - Select your desired trip duration.
    - Paste your raw itinerary components (e.g., tours, transfers, specific activities) into the text area.

4.  **Organize**: Click the "Organize Itinerary" button to generate your structured travel plan.

## Dependencies
The project relies on the following Python libraries:
- `streamlit`: For building the web application.
- `openai`: For interacting with the OpenAI API (used via OpenRouter).
- `python-dotenv`: For loading environment variables from a `.env` file.
- `requests`: For making HTTP requests to the OpenRouter API.

## License
This project is licensed under the MIT License - see the LICENSE file for details (if applicable, otherwise state "No specific license provided.").