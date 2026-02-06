import json
from google import genai
from google.genai import types

# 1. Response Schema: Defines the exact structure the AI must follow
# This ensures your app.py can always find 'detected_items', 'style_vibe', etc.
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "detected_items": {
            "type": "array",
            "items": {"type": "string"}
        },
        "fabric_weight": {
            "type": "string",
            "enum": ["light", "medium", "heavy"]
        },
        "primary_colors": {
            "type": "array",
            "items": {"type": "string"}
        },
        "style_vibe": {
            "type": "string"
        }
    },
    "required": ["detected_items", "fabric_weight", "primary_colors", "style_vibe"],
    "additionalProperties": False
}

# 2. Vision Analysis Function
def analyze_outfit_vision(
        image_bytes: bytes,
        mime_type: str,
        client: genai.Client
) -> dict:
    """
    Uses Gemini 3 Flash to extract structured fashion intelligence from an image.
    Optimized for the Gemini 3 Hackathon 2026.
    """

    prompt = (
        "Analyze this fashion image with expert precision. "
        "Identify items, fabric weight, colors, and style vibe. "
        "Return the results in the requested JSON format."
    )

    try:
        # Calling the Gemini 3 Flash Preview model
        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                        types.Part.from_bytes(
                            data=image_bytes,
                            mime_type=mime_type,
                            # Use high resolution to ensure patterns and textures are detected
                            media_resolution="media_resolution_high" 
                        )
                    ] 
                )
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RESPONSE_SCHEMA,
                # Gemini 3 Specific: Thinking configuration
                thinking_config=types.ThinkingConfig(
                    include_thoughts=True,
                    thinking_level="medium" # Balanced level for fast but accurate vision
                )
            )  
        )

        # Safety check: ensure response text exists
        if not response.text:
            return {"error": "Vision analysis failed: no response text received."}

        # Use strip() to clean any accidental whitespace from the API response
        return json.loads(response.text.strip())
    
    except json.JSONDecodeError:
        return {"error": "The model produced an invalid JSON format."}
    except Exception as e:
        return {"error": f"Vision service connection error: {str(e)}"}