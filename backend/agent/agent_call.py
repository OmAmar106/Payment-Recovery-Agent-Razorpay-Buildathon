import os
from dotenv import load_dotenv
import requests

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

HEADERS = {
    "Content-Type": "application/json",
    "X-goog-api-key": GEMINI_API_KEY,
}

def ag_call(text):

    prompt = """
You are a payment recovery decision agent.

You MUST return a JSON object with EXACTLY these three fields:

{
    "action": "",
    "delay": 0,
    "message": ""
}

Rules:

- "action" MUST be one of:
- "WAIT_AND_RETRY"
- "SHOW_MESSAGE"
- "RETRY"
- "EMAIL"
- "HUMAN_ESCALATION"

- "delay" MUST be an integer between 0 and 300.
- "message" MUST be a short customer-facing string.
- Do not return any other fields.
- Do not return markdown.
- Do not explain your reasoning.
- Return ONLY the JSON object.

Payment information:
""" + text

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent"

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    response = requests.post(url, headers=HEADERS, json=payload)

    print(response.status_code)
    print(response.json())

    # response.raise_for_status()

    return response.json()["candidates"][0]["content"]["parts"][0]["text"]