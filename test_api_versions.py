import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: API Key not found")
else:
    print("--- Testing with V1 API ---")
    try:
        # The new SDK might use different config for versioning
        client = genai.Client(api_key=api_key, http_options={'api_version': 'v1'})
        response = client.models.generate_content(model="gemini-1.5-flash", contents="Hello")
        print(f"✅ Success with v1: {response.text[:20]}...")
    except Exception as e:
        print(f"❌ Failed with v1: {e}")

    print("\n--- Testing with v1beta API ---")
    try:
        client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})
        response = client.models.generate_content(model="gemini-1.5-flash", contents="Hello")
        print(f"✅ Success with v1beta: {response.text[:20]}...")
    except Exception as e:
        print(f"❌ Failed with v1beta: {e}")
