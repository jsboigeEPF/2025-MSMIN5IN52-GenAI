import requests
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


def get_weather_data(city="Cachan", country="FR"):
    """
    Récupère les données météorologiques pour une ville donnée via l'API OpenWeather.

    Args:
        city (str): Nom de la ville (par défaut: Cachan)
        country (str): Code du pays (par défaut: FR)

    Returns:
        dict: Données météorologiques ou message d'erreur
    """
    # Récupération de la clé API depuis les variables d'environnement
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return {"error": "Clé API OpenWeather manquante dans les variables d'environnement"}

    # URL de base de l'API OpenWeather
    base_url = "http://api.openweathermap.org/data/2.5/weather"

    # Paramètres de la requête
    params = {
        "q": f"{city},{country}",
        "appid": api_key,
        "units": "metric",  # Pour obtenir la température en Celsius
        "lang": "fr"        # Pour obtenir la description en français
    }

    try:
        # Effectuer la requête HTTP
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP

        # Parser la réponse JSON
        data = response.json()

        # Extraire les informations pertinentes
        weather_info = {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "temp_min": data["main"]["temp_min"],
            "temp_max": data["main"]["temp_max"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"],
            "wind_speed": data["wind"]["speed"],
            "wind_deg": data["wind"]["deg"]
        }

        return weather_info

    except requests.exceptions.RequestException as e:
        return {"error": f"Erreur lors de la requête à l'API OpenWeather: {str(e)}"}
    except KeyError as e:
        return {"error": f"Données manquantes dans la réponse de l'API: {str(e)}"}
    except Exception as e:
        return {"error": f"Erreur inattendue: {str(e)}"}
