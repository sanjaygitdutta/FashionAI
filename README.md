👗 AI Fashion Stylist (Gemini 3)

An AI-powered personal fashion stylist that analyzes your outfit image, checks real-time weather and your calendar, and gives smart, contextual outfit recommendations using Gemini 3.

Built with:

🧠 Gemini 3 (Vision + Agentic Reasoning)

🌦️ Weather API

📅 Calendar integration

🎨 Streamlit frontend

⚙️ Modular, production-ready architecture

✨ Features

Upload your outfit photo 📸

AI analyzes clothing, fabric, colors & style

Automatically checks:

Weather conditions 🌦️

Calendar events (meetings, outings) 📅

Personalized fashion advice based on:

Occasion

Climate

Formal / casual needs

Clean UI with Streamlit

🗂️ Project Structure
fashion_agent_project/
├── .streamlit/
│   └── config.toml
├── .env
├── .gitignore
├── requirements.txt
├── README.md
│
├── app.py              # Streamlit UI (ENTRY POINT)
├── agent_logic.py      # Core Gemini agent logic
│
├── services/
│   ├── __init__.py
│   └── vision_services.py
│
└── tools/
    ├── __init__.py
    ├── weather_tool.py
    └── calendar_tool.py

🔐 Environment Variables

Create a .env file in the root folder:

GOOGLE_API_KEY=your_gemini_api_key_here
WEATHER_API_KEY=your_openweather_api_key_here


⚠️ Never commit .env to GitHub

📦 Installation
1️⃣ Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

2️⃣ Install dependencies
pip install -r requirements.txt

▶️ Run the Application

Start the Streamlit app:

streamlit run app.py


Then open in browser:

http://localhost:8501

🧠 How It Works

User uploads an outfit image

Vision Service

Detects clothes, colors, fabric & style

Agent Logic

Calls weather tool

Calls calendar tool

Uses Gemini 3 reasoning loop

Final Recommendation

Context-aware outfit advice

🛡️ Security Notes

API keys are entered securely in sidebar or .env

.gitignore blocks secrets

OAuth tokens stored locally (calendar)

🚀 Future Improvements

Outfit history & wardrobe tracking

Voice input

E-commerce outfit links

Mobile version

Multi-language support

🧑‍💻 Author

Sanjay Dutta
email-sanjoydutta1200@gmail.com
Built for learning, innovation & real-world deployment.