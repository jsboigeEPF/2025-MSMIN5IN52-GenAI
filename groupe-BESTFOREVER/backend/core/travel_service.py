import os
import json
from tavily import TavilyClient
import openai
import google.generativeai as genai

print("--- travel_service.py has been reloaded ---")

async def search_travel_options(destination: str, budget: int = None, dates: str = None, openai_client: openai.OpenAI = None, gemini_model: genai.GenerativeModel = None):
    """Searches the web for travel options using the Tavily API and summarizes results with an AI."""
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
        search_results = response['results']

        # Now, use an AI to summarize these results
        summary_prompt = f"Summarize the following travel search results for a trip to {destination} (budget: {budget}, dates: {dates}) and extract key information like flight prices, hotel options, and relevant links. Make it concise and easy to read for a user. Here are the search results: {json.dumps(search_results)}"

        if openai_client:
            # ✅ FIX: OpenAI is NOT async - remove await
            ai_response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes web search results for travel planning."},
                    {"role": "user", "content": summary_prompt}
                ],
                max_tokens=500
            )
            return ai_response.choices[0].message.content.strip()
        elif gemini_model:
            # ✅ Gemini IS async - keep await
            ai_response = await gemini_model.generate_content_async(
                [
                    {"role": "user", "parts": ["You are a helpful assistant that summarizes web search results for travel planning."]},
                    {"role": "model", "parts": ["Okay, I will summarize the search results for travel planning."]},
                    {"role": "user", "parts": [summary_prompt]}
                ]
            )
            return ai_response.text
        else:
            return json.dumps({"error": "No AI client provided for summarization."})

    except Exception as e:
        print(f"Error during Tavily search or AI summarization: {e}")
        return json.dumps({"error": str(e)})