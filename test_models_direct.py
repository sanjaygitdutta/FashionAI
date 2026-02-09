import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: API Key not found")
else:
    client = genai.Client(api_key=api_key)
    test_models = ["gemini-1.5-flash", "models/gemini-1.5-flash", "gemini-1.5-flash-latest"]
    
    for m in test_models:
        print(f"Testing model ID: {m}")
        try:
            response = client.models.generate_content(model=m, contents="Hello")
            print(f"✅ Success with {m}: {response.text[:20]}...")
        except Exception as e:
            print(f"❌ Failed with {m}: {e}")
        print("-" * 20)
