import requests

class WeatherAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"

    def get_weather_data(self, city):
        url = f"{self.base_url}/weather?q={city}&appid={self.api_key}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.status_code, "message": response.json().get("message", "Unknown error")}

    def get_forecast_data(self, city):
        url = f"{self.base_url}/forecast?q={city}&appid={self.api_key}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.status_code, "message": response.json().get("message", "Unknown error")}
