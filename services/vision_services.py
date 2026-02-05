import json
from google import genai
from google.genai import types

# response schema
# this gaarentees structured for safe output
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
    "required": [
        "detected_items",
        "fabric_weight",
        "primary_colors",
        "style_vibe"
    ],
    "additionalProperties": False
}


# vision analysis function
def analyze_outfit_vision(
        image_bytes: bytes,
        mime_type: str,
        client: genai.Client
) -> dict:
    """
    Uses Gemini 3 high-resolution mutimodal vision
    to extract structured fashion inteligence from the user's photo.
    """

    prompt = (
        "Analyze this fashion image with expert precision.\n"
        "Return ONLY valid JSON matching the required schema.\n\n"
        "Tasks:\n"
        "- Identify visible clothing items\n"
        "- Estimate fabric weight (light, medium, heavy)\n"
        "- Detect dominant colors\n"
        "- Classify overall style vibe\n"
        "- Describe fit characteristics\n"
    )

    try:
        response = client.models.generate_content(
          model="gemini-3-pro-preview",
          contents=[
              types.Content(
                 role="user",
                 parts=[
                     types.Part.from_text(prompt),
                     types.Part.from_bytes(
                         data=image_bytes,
                         mime_type=mime_type,
                         media_resolution=types.MediaResolution.MEDIA_RESOLUTION_HIGH 
                     )
                 ] 
              )
          ],
          config=type.GenerateContentConfig(
              response_mime_type="application/json",
              response_schema=RESPONSE_SCHEMA,
              thinking_config=types.ThinkingConfig(
                  thinking_level=types.ThinkingLevel.MEDIUM
              )
          )  
        )

        if not response.candidates:
            return{"error": "vision analysis failed: no response from model."}
        

        #saftey collect all text parts
        raw_json=""
        for part in response.candidates[0].context.parts:
            if hasattr(part, "text") and part.text:
                raw_json += part.text.strip()

        return json.loads(raw_json)
    
    except json.JSONDecodeError:
        return{"error": "Model returned invalid JSON format."}
    
    except Exception as e:
        return{"error": f"Vision service error: {str(e)}"}
        