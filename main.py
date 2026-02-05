import os
import uvicorn
import requests
from fastapi import FastAPI,UploadFile,File,HTTPException
from dotenv import load_dotenv
from google import genai
from google.genai import types
from tools.weather_tool import get_weather_tool
from tools.calendar_tool import get_calendar_events
from services.vision_services import analyze_outfit_vision
from agent_logic import run_fashion_agent




#load API KEYS from .env file
load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_KEY = os.getenv("WEATHER_API_KEY")

if not GEMINI_KEY or not WEATHER_KEY:
    raise ValueError("API keys are not set in the env.")

app = FastAPI(
    title="AI Fashion stylist pro",
    description="Multimodal AI stylist using Gemini 3 and real time weather data",
    version="1.0.0"
)

client = genai.Client(api_key=GEMINI_KEY)

#Declare tool for gemini
#this is tells gemini how to use function
weather_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_weather_tool",
            description="Get the current weather for a city to recommend clothing.",
            parameters={
                "type": "object",
                "properties": {
                    "city": {"type": "string","description": "name of city"}
                },
                "required":["city"]
            }
        )
    ]
)

calendar_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_calendar_events",
            description="Get today's upcoming calendar events to understand if the user has meetings or outdoor plans.",
            parameters={
                "type": "object",
                "properties": {}
            }
        )
    ]
)


@app.post("/auto_recommender/")
async def auto_recommend(city: str, image: UploadFile = File(...)):
    image_bytes = await image.read()

    messages = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(f"I am in {city}. what should i wear today?"),
                types.Part.from_bytes(data=image_bytes, mime_type=image.content_type)
            ]
        )
    ]

    system_instruction = (
        "You are an Elite AI Fashion Stylist. Follow these steps:\n"
        "1. Analyze the photo for body type and personal style.\n"
        "2. Call 'get_weather_tool' to understand the local climate.\n"
        "3. Recommend a complete outfit and Explain your reasoning.\n"
        "4. Call 'get_calendar_events' to check if the user has meetings, formal events, or outdoor activities today.\n"
        "5. Recommend an outfit suitable for body type, weather, and event importance.\n"
    )

    # The true agentic loop
    for _ in range(5):
        response = client.models.generate_content(
            model="gemini-3-pro-premium",
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction="Analyze the photo for body type and use the weather tool to recommend an outfit.",
                tools=[weather_tool, calendar_tool],
                thinking_config=types.ThinkingConfig(think_level=types.ThinkingLevel.HIGH)
            )
        )
        if not response.candidates:
            raise HTTPException(status_code=500, detail="No response from Gemini.")

        # save the model's response 
        messages.append(response.candidates[0].content)

        # look for tool calls in the response part
        function_calls = [
            part.functional_call for part in response.candidates[0].content.parts if part.functional_call
        ]

        if not function_calls:
            break

        # Execute the requested tools
        for fc in function_calls:
            if fc.name == "get_weather_tool":
                tool_result = get_weather_tool(**fc.args)

            elif fc.name == "get_calendar_events":
                tool_result = get_calendar_events()


                # send as role="tool" per protocol
                messages.append(
                    types.content(
                        role="tool",
                        parts=[types.Part.form_function_response(name=fc.name, response=tool_result)] 
                    )
                )

    # Extract final recommendation from the last parts
    recommendation_text = "".join([p.text for p in response.candidates[0].content.parts if p.text])

    return {
        "recommendation": recommendation_text,
        "metadata": {"city": city, "model": "gemini-3-pro-premium"}
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

    