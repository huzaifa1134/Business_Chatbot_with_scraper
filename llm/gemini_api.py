import requests, os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def generate_answer(prompt: str):
  if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in environment variables.")

  url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
  payload = {"contents": [{"parts": [{"text": prompt}]}]}

  res = requests.post(url, json=payload, timeout=60)
  if res.status_code != 200:
    raise Exception(f"Gemini Api Error: {res.text}")

  data = res.json()
  return data["candidates"][0]["content"]["parts"][0]["text"]