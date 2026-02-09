import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: API Key not found")
else:
    client = genai.Client(api_key=api_key)
    test_models = [
        "gemini-2.0-flash-lite", 
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash-001",
        "gemma-3-27b-it",
        "gemini-pro-latest"
    ]
    
    print("--- Probing for Working Model (No 429) ---")
    for m in test_models:
        print(f"Testing model: {m}")
        try:
            response = client.models.generate_content(model=m, contents="Hi")
            print(f"✅ WORKS! {m}: {response.text[:20]}...")
            # If we find one that works, we stop.
            break
        except Exception as e:
            print(f"❌ 429/Error: {m}")
        print("-" * 20)
