import json

def search_travel_options(destination: str, budget: int = None, dates: str = None):
    """Simulates searching for travel options and returns a JSON string with dummy data."""
    print(f"Searching for travel options to {destination} with budget {budget} and dates {dates}")
    
    # In a real application, this would call a travel API (e.g., Skyscanner, Expedia)
    dummy_data = {
        "flights": [
            {"airline": "Air France", "price": 500, "departure": "2024-12-25 08:00"},
            {"airline": "Lufthansa", "price": 450, "departure": "2024-12-25 10:00"},
        ],
        "hotels": [
            {"name": "Hotel de Paris", "price_per_night": 150, "rating": 4.5},
            {"name": "Grand Hotel", "price_per_night": 200, "rating": 4.8},
        ]
    }
    
    return json.dumps(dummy_data)
