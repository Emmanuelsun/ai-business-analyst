import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("No key found. Check your .env file.")
    raise SystemExit

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
    contents="Say hello to a shop owner in one short sentence.",
)

print(response.text)