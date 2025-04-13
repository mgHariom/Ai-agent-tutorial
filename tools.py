import datetime
import time
import requests

def get_current_time():
    return {"time": datetime.datetime.now().strftime("%H:%M:%S")}

def set_reminder(seconds: int):
    time.sleep(seconds)
    return {"message": f"⏰ Reminder after {seconds} seconds is done!"}

def tell_joke():
    return {"joke": "Why did the computer show up at work late? It had a hard drive."}

def get_weather(city: str) -> str:
    """
    Fetches the current weather for the given city using wttr.in.
    """
    try:
        url = f"https://wttr.in/{city}?format=3"  # Just "City: Weather, Temp"
        response = requests.get(url)

        if response.status_code == 200:
            return response.text.strip()
        else:
            return f"Could not fetch weather for {city}. Response code: {response.status_code}"
    except Exception as e:
        return f"Error fetching weather: {str(e)}"