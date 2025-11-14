
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llm.manager import get_best_answer
from rag.embeddings import build_vector_store, get_context
from scraping.extractor import crawl_website, get_logo, save_faiss_index, load_faiss_index, save_chunks, load_chunks
import os
from fastapi.middleware.cors import CORSMiddleware
import pickle

app = FastAPI(
    title="Smart Web Chatbot(Powered by Gemini)",
    description="Scrapes websites and answers via Hugging Face (default) with Gemini fallback. Supports dynamic company adaptation with logo.",
    version="1.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {}

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

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
    domain = req.company_url.replace("https://", "").replace("http://", "").replace("/", "")
    folder_path = os.path.join(DATA_DIR, domain)
    os.makedirs(folder_path, exist_ok=True)
    index_path = os.path.join(folder_path, "index.faiss")
    chunks_path = os.path.join(folder_path, "chunks.pkl")

    if os.path.exists(index_path) and os.path.exists(chunks_path):
        index = load_faiss_index(index_path)
        chunks = load_chunks(chunks_path)
    else:
        pages = crawl_website(req.company_url, max_pages=15)
        if not pages:
            raise HTTPException(status_code=400, detail="Failed to extract text.")
        all_text = "\n".join([p['text'] for p in pages])
        chunks, index = build_vector_store(all_text)
        save_faiss_index(index, index_path)
        save_chunks(chunks, chunks_path)

    logo_url = get_logo(req.company_url)
    sessions[req.user_id] = {
        "company_name": req.company_name,
        "company_url": req.company_url,
        "company_logo": logo_url,
        "chunks": chunks,
        "index": index,
        "history": []
    }

    return {
        "message": "Scraping complete.",
        "chunks": len(chunks),
        "company_logo": logo_url
    }

@app.post("/ask")
def ask_question(req: QuestionRequest):
    session = sessions.get(req.user_id)
    if not session:
        prompt= f"User Asked: {req.question}\nAnswer as a helpful assistant."
        answer = get_best_answer(prompt)
        return{
            "answer": answer,
            "company_name": None,
            "company_logo": None,
            "context_used": []
        }
        

    context_chunks = get_context(req.question, session)
    context_text = "\n\n".join(context_chunks)

    history_text = ""
    for h in session['history']:
        history_text += f"User: {h['user']}\nBot: {h['bot']}\n"

    prompt = f"""
You are the official chatbot for {session['company_name']}.
Use the following information to answer accurately and in company's tone:

Previous chat history:
{history_text}

Relevant information from website:
{context_text}

Current question: {req.question}
"""
    try:
      answer = get_best_answer(prompt)
    except Exception as e:
      if "RESOURCE_EXHAUSTED" in str(e):
        answer = "Sorry, the system is currently experiencing high load. Please try again later."
      else:
        answer = f"Sorry, I couldn't get an answer at this time. {str(e)}"

    session['history'].append({"user": req.question, "bot": answer})
    if len(session['history']) > 6:
        session['history'] = session['history'][-6:]

    return {
        "answer": answer,
        "company_name": session["company_name"],
        "company_logo": session["company_logo"],
        "context_used": context_chunks[:2]
    }
