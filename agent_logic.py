import streamlit as st
import json
from google import genai
from google.genai import types
from tools.weather_tool import get_weather_tool
from tools.calendar_tool import get_calendar_events

def run_fashion_agent(
    user_prompt: str,
    image_data: dict,
    client: genai.Client
) -> str:
    """
    Core agentic reasoning loop for AI Fashion Stylist.
    Outputs structured JSON with visual observations, decision winner, and tradeoffs.
    """

    system_instruction = (
        "You are an expert AI Fashion Stylist.\n\n"
        "You MUST base your final recommendation on:\n"
        "1. Vision analysis of the user's clothing (provided in image_data)\n"
        "2. Current weather conditions\n"
        "3. The user's calendar events\n\n"
        "RULES:\n"
        "- ALWAYS check weather and calendar using tools before answering.\n"
        "- If a formal meeting exists, prioritize professional outfits.\n"
        "- Compare options if multiple items are found. Declare a 'winner'.\n"
        "- Provide your response in strictly valid JSON format matching the schema."
    )

    tools = [
        types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name="get_weather_tool",
                    description="Get real-time weather for a city to provide accurate clothing advice.",
                    parameters={
                        "type": "OBJECT",
                        "properties": {
                            "city": {"type": "STRING", "description": "The name of the city, e.g., 'Delhi'"}
                        },
                        "required": ["city"]
                    }
                ),
                types.FunctionDeclaration(
                    name="get_calendar_events",
                    description="Get the user's upcoming calendar events to understand the dress code context.",
                    parameters={"type": "OBJECT", "properties": {}, "required": []}
                )
            ]
        )
    ] 

    # Initial context
    messages = [
        types.Content(
            role="user",
            parts=[types.Part(text=f"Vision Data: {json.dumps(image_data)}\nUser Request: {user_prompt}")]
        )  
    ]

    # Agentic loop (Max 5 turns)
    for i in range(5):
        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=tools,
                # --- STRUCTURED OUTPUT SCHEMA ---
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "visual_observations": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "context_understanding": {"type": "STRING"},
                        "reasoning_steps": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "winner": {"type": "STRING"},
                        "reason": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "tradeoffs": {
                            "type": "OBJECT",
                            "properties": {
                                "Outfit A": {"type": "STRING"},
                                "Outfit B": {"type": "STRING"}
                            }
                        },
                        "final_recommendation": {"type": "STRING"},
                    },
                    "required": [
                        "visual_observations", 
                        "context_understanding", 
                        "reasoning_steps", 
                        "winner", 
                        "reason", 
                        "tradeoffs", 
                        "final_recommendation"
                    ]
                },
                thinking_config=types.ThinkingConfig(
                    include_thoughts=True,
                    thinking_level="high" 
                )
            )
        )

        if not response.candidates:
            return "No response generated."
        
        model_content = response.candidates[0].content
        messages.append(model_content)

        # Extract tool calls
        tool_calls = [part.function_call for part in model_content.parts if part.function_call]

        # Final Answer check
        if not tool_calls:
            final_text = "".join(part.text for part in model_content.parts if part.text)
            return final_text

        # Execute tools
        tool_parts = []
        for fc in tool_calls:
            with st.status(f"🔍 Agent is consulting {fc.name}...", expanded=False):
                if fc.name == "get_weather_tool":
                    result = get_weather_tool(**fc.args)
                elif fc.name == "get_calendar_events":
                    result = get_calendar_events()
                else:
                    result = {"error": "Unknown tool"}

                tool_parts.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=fc.name,
                            response={"result": result}
                        )
                    )
                )

        # Send tool results back to model
        messages.append(types.Content(role="user", parts=tool_parts))

    return "Max depth reached."