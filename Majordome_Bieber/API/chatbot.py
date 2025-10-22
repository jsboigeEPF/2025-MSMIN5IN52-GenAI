from openai import OpenAI
from dotenv import load_dotenv
import os

from Calendar_API import list_events
from Gmail_API import readMail
from googleapiclient.discovery import build
from login import get_credentials

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


def get_chatbot_response(query: str) -> str:
    """
    Get the chatbot response from OpenRouter.
    """
    creds = get_credentials()
    calendar_service = build("calendar", "v3", credentials=creds)

    # Fetch data from Google APIs
    calendar_events = list_events(calendar_service)
    emails = readMail(10)

    # Format the data as context
    context = "Here is some information about the user:\n\n"
    context += "Next calendar events:\n"
    for event in calendar_events:
        context += f"- {event['summary']} at {event['start']}\n"
    context += "\n"
    context += "Last emails:\n"
    for email in emails:
        context += f"- From: {email['from']}, Subject: {email['subject']}\n"
    context += "Fais ta réponse en français.\n"
    context += "La réponse doit impérativement être de 2 phrases maximum, fais au plus succint"
    # Send the query and context to OpenRouter
    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Your name is Justin Bieber the singer. You are a butler. You have access to the user's calendar and emails. Here is the context:\n" + context,
            },
            {"role": "user", "content": query},
        ],
    )
    return response.choices[0].message.content
