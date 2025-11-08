from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llm.manager import get_best_answer
from rag.embeddings import build_vector_store, get_context
from scraping.extractor import extract_text, get_logo
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
  title="Smart Web Chatbot(Powered by HF and Gemini)",
  description="Scrapes websites and answers via Hugging Face (default) with Gemini fallback. Supports dynamic company adaptation with logo.",
  version="1.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {}

class ScrapeRequest(BaseModel):
  user_id: str
  company_name: str
  company_url: str

class QuestionRequest(BaseModel):
  user_id: str
  question: str

@app.get("/health")
def health_check():
    return {"status": "ok"} 

@app.post("/scrape")
def scrape_page(req: ScrapeRequest):
  text = extract_text(req.company_url)
  if not text or len(text) < 100:
    raise HTTPException(
       status_code=400,
       detail="Failed to extract text. Text is too short.")
  
  chunks, index = build_vector_store(text)
  logo_url = get_logo(req.company_url)

  sessions[req.user_id] = {
    "company_name": req.company_name,
    "company_logo": logo_url,
    "company_url": req.company_url,
    "chunks": chunks,
    "index": index
  }

  return {
    "message": "Scraping complete.",
    "chunks": len(chunks),
    "company_logo": logo_url
  }
@app.post("/ask")
def ask_question(req: QuestionRequest):
    try:
        session = sessions.get(req.user_id)
        if not session:
            raise HTTPException(
                status_code=400,
                detail="No session found for this user. Please scrape a company first."
            )

        print(f"[DEBUG] Session found for user: {req.user_id}")
        print(f"[DEBUG] Question: {req.question}")
        
        context = get_context(req.question, session)
        print(f"[DEBUG] Context retrieved: {len(context)} chunks")
        
        context_text = "\n\n".join(context)

        prompt = f"""You are now the official chatbot for {session['company_name']}.
Use the following information to answer accurately and in the company's tone:

{context_text}

Question: {req.question}"""
        
        print(f"[DEBUG] Getting answer from LLM...")
        answer = get_best_answer(prompt)
        print(f"[DEBUG] Answer received: {len(answer)} chars")
        
        return {
            "answer": answer,
            "company_name": session["company_name"],
            "company_logo": session["company_logo"],
            "context_used": context[:2]
        }
    except HTTPException as e:
        print(f"[ERROR] HTTP Exception: {e.detail}")
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
