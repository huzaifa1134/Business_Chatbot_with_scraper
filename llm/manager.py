from llm.huggingface_api import generate_answer as hf_answer
from llm.gemini_api import generate_answer as gemini_answer

def get_best_answer(prompt: str):
  try:
    print(f"Using Hugging face as Prmary model...")
    return hf_answer(prompt)
  except Exception as e:
    print(f"[WARN] Hugging Face Model failed {e}")
    try:
      print(f"[INFO] Falling back to Gemini model...")
      return gemini_answer(prompt)
    except Exception as e2:
      return f"Both models failed {str(e2)}"