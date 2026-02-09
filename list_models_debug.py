import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found in .env")
else:
    try:
        client = genai.Client(api_key=api_key)
        print("--- Listing Available Models ---")
        for model in client.models.list(config={'page_size': 50}):
            print(f"Model Name: {model.name}")
            print(f"Supported Methods: {model.supported_actions}")
            print("-" * 30)
    except Exception as e:
        print(f"Error: {e}")
