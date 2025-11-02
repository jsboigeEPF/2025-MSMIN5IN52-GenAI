import os
import json
from tavily import TavilyClient

async def search_travel_options(destination: str, budget: int = None, dates: str = None):
    """Searches the web for travel options using the Tavily API."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return json.dumps({"error": "TAVILY_API_KEY not found in .env"})

    tavily = TavilyClient(api_key=api_key)
    
    query = f"flights and hotels in {destination}"
    if dates:
        query += f" around {dates}"
    if budget:
        query += f" with a budget of {budget}"

    print(f"Performing Tavily search with query: {query}")
    
    try:
        response = tavily.search(query=query, search_depth="advanced")
        return json.dumps(response['results'])
    except Exception as e:
        print(f"Error during Tavily search: {e}")
        return json.dumps({"error": str(e)})
