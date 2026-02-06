👗 Gemini 3 Smart Fashion Stylist
An advanced, context-aware AI Agent that acts as a personal fashion consultant. This project goes beyond simple chat by fusing Computer Vision, Real-time Weather Grounding, Schedule Awareness, and Voice Interactivity.

🧠 The "Gemini 3" Advantage
This application leverages the latest 2026 capabilities of the Gemini 3 model series:

Reasoning-First Agent: Uses thinking_level="high" to evaluate outfit suitability based on environmental factors before responding.

Multimodal Fusion: Analyzes user-uploaded images via gemini-3-flash to identify specific clothing items, textures, and styles.

Built-in Grounding: Utilizes Google Search grounding to suggest current fashion trends and retail availability.

✨ Key Features
🔍 Vision Analysis: Automatically detects clothing items from your photos.

🌦️ Weather Integration: Calls the OpenWeatherMap API to ensure your outfit matches the local forecast (temp, rain, humidity).

📅 Calendar Sync: Integrates with Google Calendar to understand your day's "vibe" (e.g., Formal Meeting vs. Casual Coffee).

🎙️ Voice & Audio: Support for voice-to-text input and natural AI-generated audio responses using gTTS.

🚀 Performance: Dual-service architecture using FastAPI for high-speed logic and Streamlit for a reactive UI.

🛠️ Project Architecture
Plaintext
├── app.py              # Reactive Streamlit Frontend (Voice/Vision UI)
├── main.py             # FastAPI Backend (Agent Orchestrator)
├── agent_logic.py      # Core Gemini 3 Reasoning & Tool Execution Loop
├── vision_services.py  # Image processing logic
├── requirements.txt    # Project dependencies
└── tools/              # Modular Agent Tools
    ├── weather_tool.py # OpenWeatherMap API Integration
    └── calendar_tool.py# Google Calendar API Integration
🚀 Setup & Installation
1. Clone the Repository
Bash
git clone <your-repo-url>
cd fashion-stylist-agent
2. Install Dependencies
Bash
pip install -r requirements.txt
3. Environment Configuration
Create a .env file in the root directory and add your keys:

Code snippet
GOOGLE_API_KEY=your_gemini_key
WEATHER_API_KEY=your_openweathermap_key # From https://home.openweathermap.org/
4. Run the Application
Bash
# Start the Backend
uvicorn main:app --reload

# Start the Frontend (New Terminal)
streamlit run app.py
🌦️ Data Grounding Logic
The agent doesn't guess—it verifies. When a user asks "What should I wear?", the agent:

Calls get_weather_tool to check the Real-time Weather.

Calls get_calendar_events to check the User's Schedule.

Cross-references these data points with the Vision Data from the outfit photo to provide a final, grounded recommendation.

Developed for the 2026 Gemini 3 Developer Hackathon.