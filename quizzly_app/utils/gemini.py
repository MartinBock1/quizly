import os
from google import genai


def gemini_generate_content(prompt, model="gemini-2.5-flash"):
    """
    Sends a prompt to the Gemini API and returns the generated text.
    The API key is automatically loaded from the .env file.
    Args:
        prompt (str): The prompt to send to Gemini.
        model (str): The Gemini model to use (default: "gemini-2.5-flash").
    Returns:
        str: The generated text response from Gemini.
    """
    api_key = os.getenv('GEMINI_API_KEY')
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    return response.text
