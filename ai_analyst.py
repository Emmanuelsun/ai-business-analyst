import os
import re
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()


def _get_setting(name):
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st
        return st.secrets[name]
    except Exception:
        return None


def get_insights(summary):
    api_key = _get_setting("GEMINI_API_KEY")
    if not api_key:
        return "No API key found. Check your .env file."

    client = genai.Client(api_key=api_key)
    facts = json.dumps(summary, indent=2)

    prompt = f"""You are a friendly business analyst helping a small shop owner.
Below are FACTS that were calculated by a computer from the owner's sales file.

RULES:
1. Use ONLY the numbers in the FACTS. Never invent, guess or estimate any number.
2. Write in simple, plain words that a shop owner can understand.
3. The data covers only a few days and a small number of sales, so do not claim long-term trends. Say clearly when the data is too small to be sure.
4. Amounts are in Nigerian Naira.

Write:
- An overview in 2 sentences.
- 3 key insights.
- 3 practical recommendations.
Keep it under 200 words.

FACTS:
{facts}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
        )
        return response.text
    except Exception as error:
        return f"The AI could not answer right now: {error}"


def find_unverified_numbers(text, summary):
    facts_text = json.dumps(summary)
    allowed = {float(n.replace(",", "")) for n in re.findall(r"\d[\d,]*\.?\d*", facts_text)}

    cleaned = re.sub(r"(?m)^\s*\d+\.\s", "", text)
    found = re.findall(r"\d[\d,]*\.?\d*", cleaned)

    unverified = []
    for number in found:
        value = float(number.replace(",", ""))
        if value not in allowed:
            unverified.append(number)
    return unverified