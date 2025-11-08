import requests, os
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN= os.getenv("HF_TOKEN")

def generate_answer(prompt: str):
  if not HF_TOKEN:
    raise ValueError("HF_TOKEN is not set in environment variables.")
  headers = {"Authorization":f"Bearer {HF_TOKEN}"}
  model_url = "https://api-inference.huggingface.co/models/google/gemma-2b-it"
  payload = {"inputs": prompt}

  res = requests.post(model_url, headers=headers, json=payload, timeout=60)
  if res.status_code != 200:
    raise Exception(f"Huggingface Api Error: {res.text}")

  try:
    data = res.json()
    return data[0]["generated_text"]
  except Exception:
    return res.text