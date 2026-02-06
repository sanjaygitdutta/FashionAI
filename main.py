import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from dotenv import load_dotenv
from google import genai
from google.genai import types
from tools.weather_tool import get_weather_tool
from tools.calendar_tool import get_calendar_events

# Load API KEYS
load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_KEY = os.getenv("WEATHER_API_KEY")

if not GEMINI_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the .env file.")

app = FastAPI(
    title="AI Fashion Stylist Pro",
    description="Backend API for Multimodal AI Stylist",
    version="1.0.0"
)

client = genai.Client(api_key=GEMINI_KEY)

# Declare tools
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

@app.post("/auto_recommender/")
async def auto_recommend(city: str, image: UploadFile = File(...)):
    image_bytes = await image.read()

    # Fixed: Added 'text=' keyword
    messages = [
        types.Content(
            role="user",
            parts=[
                types.Part(text=f"I am in {city}. what should i wear today?"),
                types.Part.from_bytes(data=image_bytes, mime_type=image.content_type)
            ]
        )
    ]

    system_instruction = (
        "You are an Elite AI Fashion Stylist. Analyze the photo for body type, "
        "check weather and calendar, and recommend a complete outfit."
    )

    # Agentic loop
    for _ in range(5):
        response = client.models.generate_content(
            model="gemini-3-pro-preview", # Check if your plan uses 'preview' or 'latest'
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[weather_tool, calendar_tool],
                thinking_config=types.ThinkingConfig(
                    include_thoughts=True # Ensure model can 'think'
                )
            )
        )
        
        if not response.candidates:
            raise HTTPException(status_code=500, detail="No response from Gemini.")

        # Save model response
        model_content = response.candidates[0].content
        messages.append(model_content)

        # Fixed: Changed functional_call to function_call
        function_calls = [
            part.function_call for part in model_content.parts if part.function_call
        ]

        if not function_calls:
            break

        # Execute tools
        tool_parts = []
        for fc in function_calls:
            if fc.name == "get_weather_tool":
                tool_result = get_weather_tool(**fc.args)
            elif fc.name == "get_calendar_events":
                tool_result = get_calendar_events()
            else:
                tool_result = {"error": "Unknown tool"}

            # Fixed: Changed form_function_response to from_function_response
            tool_parts.append(
                types.Part.from_function_response(name=fc.name, response=tool_result)
            )

        # Fixed: Capitalized Content and moved outside tool loop
        messages.append(types.Content(role="tool", parts=tool_parts))

    # Extract final text
    recommendation_text = "".join([p.text for p in response.candidates[0].content.parts if p.text])

    return {
        "recommendation": recommendation_text,
        "metadata": {"city": city, "model": "gemini-3-pro"}
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)