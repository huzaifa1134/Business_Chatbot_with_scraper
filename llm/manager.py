from llm.gemini_api import generate_answer as gemini_answer

def get_best_answer(prompt: str):
    try:
        print(f"[INFO] Trying Gemini API...")
        answer = gemini_answer(prompt)
        print(f"[SUCCESS] Got answer from Gemini")
        return answer
    except Exception as e:
        print(f"[WARN] Gemini failed: {e}")
        return f"Sorry, I couldn't get an answer at this time {str(e)}."