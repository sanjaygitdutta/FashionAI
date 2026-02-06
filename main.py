import os
import json
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from dotenv import load_dotenv
from pydantic import BaseModel
from google import genai
from google.genai import types

# Load Custom Tools
from tools.weather_tool import get_weather_tool
from tools.calendar_tool import get_calendar_events

# Load API KEYS
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the .env file.")

app = FastAPI(
    title="AI Fashion Stylist Pro",
    description="Backend API for Multimodal AI Stylist",
    version="1.0.0"
)

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


# --- 1. SCHEMAS ---
class StyleRequest(BaseModel):
    city: str
    occasion: str

# --- 2. TOOL DECLARATIONS ---
weather_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_weather_tool",
            description="Get current weather for a city.",
            parameters={
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"]
            }
        )
    ]
)

calendar_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_calendar_events",
            description="Get today's calendar events.",
            parameters={"type": "object", "properties": {}}
        )
    ]
)

# --- 3. THE CORE AGENT LOGIC ---
async def run_fashion_agent(city: str, occasion: str, image_bytes: bytes, mime_type: str):
    """Executes the agentic loop with tool usage and vision analysis."""
    messages = [
        types.Content(
            role="user",
            parts=[
                types.Part(text=f"Location: {city}. Event/Occasion: {occasion}. What should I wear today?"),
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            ]
        )
    ]

    system_instruction = (
        "You are an Elite AI Fashion Stylist. Analyze the photo for body type and style, "
        "check weather and calendar using tools, and recommend a complete outfit. "
        "IMPORTANT: You must return your final answer in valid JSON format only, "
        "with keys: 'recommendation', 'winner_outfit', and 'reasoning'."
    )

    # Agentic loop (Max 5 iterations)
    for _ in range(5):
        response = client.models.generate_content(
            model="gemini-2.0-flash", # Optimized for speed and tool use in 2026
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[weather_tool, calendar_tool],
                thinking_config=types.ThinkingConfig(include_thoughts=True)
            )
        )
        
        if not response.candidates:
            raise HTTPException(status_code=500, detail="Gemini failed to respond.")

        model_content = response.candidates[0].content
        messages.append(model_content)

        function_calls = [part.function_call for part in model_content.parts if part.function_call]

        if not function_calls:
            # Loop ends when model no longer requests tools
            break

        tool_parts = []
        for fc in function_calls:
            if fc.name == "get_weather_tool":
                tool_result = get_weather_tool(**fc.args)
            elif fc.name == "get_calendar_events":
                tool_result = get_calendar_events()
            else:
                tool_result = {"error": "Unknown tool"}

            tool_parts.append(types.Part.from_function_response(name=fc.name, response=tool_result))

        messages.append(types.Content(role="tool", parts=tool_parts))

    return "".join([p.text for p in response.candidates[0].content.parts if p.text])

# --- 4. ENDPOINTS ---

@app.post("/recommend")
async def get_style(
    city: str = Form(...),
    occasion: str = Form(...),
    image: UploadFile = File(...)
):
    """Structured endpoint that handles Multipart Form (Image + Text)."""
    try:
        # Validate input via Pydantic
        request_data = StyleRequest(city=city, occasion=occasion)
        image_bytes = await image.read()
        
        # Run the AI Agent
        result_string = await run_fashion_agent(
            city=request_data.city,
            occasion=request_data.occasion,
            image_bytes=image_bytes,
            mime_type=image.content_type
        )
        
        # Parse AI string to JSON to avoid escaping characters in the response
        try:
            return json.loads(result_string)
        except json.JSONDecodeError:
            return {"recommendation": result_string, "status": "partial_json_failure"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stylist Service Error: {str(e)}")

@app.post("/auto_recommender/")
async def auto_recommend(city: str, image: UploadFile = File(...)):
    """Legacy endpoint for backward compatibility."""
    image_bytes = await image.read()
    result = await run_fashion_agent(city, "general styling", image_bytes, image.content_type)
    return {"recommendation": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)