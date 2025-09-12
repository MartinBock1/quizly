import os
from google import genai


def gemini_generate_content(prompt, model="gemini-2.5-flash"):
    """
    Sendet ein Prompt an Gemini und gibt den Text zurück.
    Der API-Key wird automatisch aus der .env geladen.
    """
    api_key = os.getenv('GEMINI_API_KEY')
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    return response.text
