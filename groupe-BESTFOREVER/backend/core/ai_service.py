import os
import json
from dotenv import load_dotenv
import openai
import google.generativeai as genai
from typing import List
from . import travel_service

# Load environment variables from .env file
load_dotenv()

SYSTEM_MESSAGES = {
    "en-US": "You are a helpful travel planning assistant. Your goal is to gather information from the user to help them plan a trip. Start by asking clarifying questions to understand their needs, such as destination, budget, travel dates, and interests. You are in the US. Once you have enough information, use the available tools to search for travel options.",
    "fr-FR": "Vous êtes un assistant de planification de voyage utile. Votre objectif est de recueillir des informations auprès de l'utilisateur pour l'aider à planifier un voyage. Commencez par poser des questions de clarification pour comprendre ses besoins, tels que la destination, le budget, les dates de voyage et les centres d'intérêt. Vous êtes en France. Une fois que vous avez suffisamment d'informations, utilisez les outils disponibles pour rechercher des options de voyage."
}

# OpenAI Tools Definition
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_travel_options",
            "description": "Search for travel options like flights and hotels based on user criteria.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "The destination city, e.g., Paris"
                    },
                    "budget": {
                        "type": "number",
                        "description": "The budget for the trip"
                    },
                    "dates": {
                        "type": "string",
                        "description": "The desired travel dates, e.g., 2024-12-25 to 2025-01-02"
                    }
                },
                "required": ["destination"]
            }
        }
    }
]

# Gemini Tools Definition
GEMINI_TOOLS = {
    "function_declarations": [
        {
            "name": "search_travel_options",
            "description": "Search for travel options like flights and hotels based on user criteria.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "destination": {"type": "STRING", "description": "The destination city, e.g., Paris"},
                    "budget": {"type": "NUMBER", "description": "The budget for the trip"},
                    "dates": {"type": "STRING", "description": "The desired travel dates, e.g., 2024-12-25 to 2025-01-02"}
                },
                "required": ["destination"]
            }
        }
    ]
}

class AIService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_KEY")
        self.gemini_api_key = os.getenv("GEMINI_KEY")

        if self.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
            print("OpenAI client initialized.")
        else:
            self.openai_client = None
            print("Warning: OPENAI_KEY not found in .env. OpenAI service will not be available.")

        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            print("Gemini API key loaded.")
        else:
            print("Warning: GEMINI_KEY not found in .env. Gemini service will not be available.")

    async def list_gemini_models(self):
        # ... (code for listing models remains the same)
        pass

    async def get_openai_response(self, history: List[dict], session_id: str, language: str) -> str:
        if not self.openai_client:
            return "OpenAI service is not configured. Please provide OPENAI_KEY in .env."
        try:
            system_message = SYSTEM_MESSAGES.get(language, SYSTEM_MESSAGES["en-US"])
            messages = [{"role": "system", "content": system_message}] + [
                {"role": "assistant" if not msg.isUser else "user", "content": msg.text}
                for msg in history
            ]
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                tools=OPENAI_TOOLS,
                tool_choice="auto"
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if tool_calls:
                messages.append(response_message)
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    if function_name == "search_travel_options":
                        function_response = await travel_service.search_travel_options(
                            openai_client=self.openai_client,
                            destination=function_args.get("destination"),
                            budget=function_args.get("budget"),
                            dates=function_args.get("dates")
                        )
                        messages.append(
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": function_name,
                                "content": function_response,
                            }
                        )
                
                second_response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                )
                return second_response.choices[0].message.content

            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return f"Error from OpenAI: {e}"

    async def get_gemini_response(self, history: List[dict], session_id: str, language: str) -> str:
        if not self.gemini_api_key:
            return "Gemini service is not configured. Please provide GEMINI_KEY in .env."
        try:
            system_message = SYSTEM_MESSAGES.get(language, SYSTEM_MESSAGES["en-US"])
            model = genai.GenerativeModel(
                'gemini-flash-latest',
                system_instruction=system_message,
                tools=GEMINI_TOOLS
            )
            
            gemini_history = [
                {"role": "user" if msg.isUser else "model", "parts": [msg.text]}
                for msg in history
            ]
            
            response = await model.generate_content_async(gemini_history)

            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                part = response.candidates[0].content.parts[0]
                if hasattr(part, 'function_call') and part.function_call:
                    function_call = part.function_call
                    function_name = function_call.name
                    function_args = function_call.args
                    
                    if function_name == "search_travel_options":
                        function_response = await travel_service.search_travel_options(
                            gemini_model=model,
                            destination=function_args["destination"],
                            budget=function_args.get("budget"),
                            dates=function_args.get("dates")
                        )
                        
                        # Append the tool response to the history
                        gemini_history.append({"role": "model", "parts": [part]})
                        gemini_history.append({
                            "role": "user",
                            "parts": [
                                {
                                    "function_response": {
                                        "name": "search_travel_options",
                                        "response": {"content": function_response}
                                    }
                                }
                            ]
                        })

                        # Send the updated history back to the model
                        second_response = await model.generate_content_async(gemini_history)
                        if second_response.candidates and second_response.candidates[0].content.parts:
                            return second_response.candidates[0].content.parts[0].text
                        else:
                            return "I was unable to process the search results."

            if response.candidates and response.candidates[0].content.parts:
                return response.candidates[0].content.parts[0].text
            else:
                return "I am unable to provide a response at this time."

        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return f"Error from Gemini: {e}"

    async def get_ai_response(self, model_name: str, history: List[dict], session_id: str, language: str) -> str:
        print(f"AI Service received history for session: {session_id} using model: {model_name} with language: {language}")
        if model_name.lower() == "openai":
            return await self.get_openai_response(history, session_id, language)
        elif model_name.lower() == "gemini":
            return await self.get_gemini_response(history, session_id, language)
        else:
            return f"Invalid AI model specified: {model_name}. Please choose 'openai' or 'gemini'."
