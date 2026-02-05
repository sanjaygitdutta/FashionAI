import os
import requests
from dotenv import load_dotenv

#load keys if testing this file directly
load_dotenv()
WEATHER_KEY = os.getenv("WEATHER_API_KEY")

def get_weather_tool(city: str) -> dict:
    """
    Fetches real-time weather from OpenweatherMap.
    
    Args:
        city (str): the name of the city(e.g., "kolkata", "Delhi").
        
    Returns:
        dict: weather data or error message.
    """
    if not WEATHER_KEY:
        return{"error": "WEATHER_API_KEY is not found in enveronment."}
    
    #OpenweatherMap current weather URL
    url = "http://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": WEATHER_KEY,
        "units": "metric" #standerdizes to celsius
    }

    try:
        # 5 second timeout to prevent the agent from hanging
        response = requests.get(params=params, url=url, timeout=5)
        data = response.json()

        if response.status_code == 200:
            return{
                "city": data.get("name"),
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "condition": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "success": True
            }
        else:
            #handle specific API errors(404 city not found)
            error_msg = data.get("message", "Unknown API error occurred")
            return{"error": f"Weather API error:{error_msg}", "success": False}
        
    except requests.exceptions.Timeout:
        return{"error": "Weather API request timed out.", "success": False}
    except Exception as e:
        return{"error": f"Unexpected condition error: {str(e)}", "success": False}
    
#independent testing
if __name__ == "__main__":
    test_city = "kolkata"
    print(f"Testing weather tool for {test_city}...")
    print(get_weather_tool(test_city))
