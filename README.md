# 👗 AI Fashion Stylist Pro (Gemini 3 Agent)

An autonomous, multimodal AI stylist that uses **Gemini 3 Pro** to analyze your wardrobe and recommend the perfect outfit by checking real-time weather and your personal calendar.

## 🚀 Unique Features
- **Agentic Reasoning**: Unlike standard apps, this uses a multi-step "Thought Loop" to verify data before suggesting an outfit.
- **High-Fidelity Vision**: Leverages Gemini 3's `MEDIA_RESOLUTION_HIGH` to detect fabric textures (linen vs. wool) and garment weight.
- **Tool Integration**: Automatically calls custom Python tools for **OpenWeather API** and **Google Calendar API**.
- **Context-Aware**: Knows if you're heading to a rainy hike or a sunny boardroom meeting.

---

## 🛠️ Project Structure
- `main.py`: The FastAPI server and entry point.
- `agent_logic.py`: The core "Brain" that manages the reasoning loop and tool calls.
- `weather_tool.py`: Connects to OpenWeatherMap for live climate data.
- `calendar_tool.py`: Connects to Google Calendar for schedule awareness.
- `services/vision_services.py`: Dedicated multimodal service for clothing analysis.

---

## ⚙️ Setup Instructions

### 1. Environment Variables
Create a `.env` file in the root directory and add your keys:
```env
GEMINI_API_KEY=your_google_ai_studio_key
WEATHER_API_KEY=your_openweather_key