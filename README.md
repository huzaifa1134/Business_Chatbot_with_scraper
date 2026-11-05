# Smart Web Chatbot — Business Assistant with Website Scraper

Give it a company's website and it builds a chatbot that answers questions about that business. The back end crawls the site, indexes the content in a FAISS vector store, and uses Google Gemini to answer from the retrieved context. A Streamlit front end offers a general chat tab and a business-assistant tab.

## Features

- **Website crawling** — crawls up to 15 pages of a site, extracting readable text with newspaper3k and falling back to BeautifulSoup.
- **Retrieval-augmented answers (RAG)** — text is chunked, indexed in FAISS, and the top matching chunks are passed to Gemini as context.
- **Per-company assistants** — each user session gets its own assistant, including the company name and logo/favicon.
- **Index caching** — FAISS indexes and chunks are saved per domain under `data/`, so a site is only scraped once.
- **Two modes** — a general chatbot and a business assistant, available as tabs in the UI.
- **REST API** — FastAPI back end with interactive docs at `/docs`.

## Architecture

```
Streamlit UI (app.py)
      │  HTTP
      ▼
FastAPI (main.py)
 ├── POST /scrape ──► scraping/extractor.py ──► crawl pages, extract text, find logo
 │                    rag/embeddings.py      ──► chunk text, embed, build FAISS index
 ├── POST /ask    ──► rag/embeddings.py      ──► retrieve top-k chunks
 │                    llm/manager.py         ──► Gemini 2.0 Flash answers with context
 └── GET  /health
```

## Tech Stack

Python · FastAPI · Streamlit · FAISS · Google Gemini API · BeautifulSoup · newspaper3k · Playwright

## Getting Started

```bash
git clone https://github.com/huzaifa1134/Business_Chatbot_with_scraper.git
cd Business_Chatbot_with_scraper

python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Start the API and the UI in two terminals:

```bash
uvicorn main:app --reload --port 8000     # back end
streamlit run app.py                      # front end
```

Then open the Streamlit URL, go to **Business Assistant**, enter a company name, its website URL, and a user ID, click **Scrape and create assistant**, and start asking questions.

## API

| Method | Endpoint | Body | Description |
|---|---|---|---|
| POST | `/scrape` | `user_id`, `company_name`, `company_url` | Crawl a site and build its index |
| POST | `/ask` | `user_id`, `question` | Ask the assistant a question |
| GET | `/health` | — | Health check |

## Notes

- The default embedding in `rag/embeddings.py` is a lightweight deterministic hash-based vector, so the project runs without downloading a model. For true semantic retrieval, enable the `sentence-transformers` embedding that is already stubbed out in that file.

## Author

**Huzaifa Jawed** — [GitHub](https://github.com/huzaifa1134) · [LinkedIn](https://www.linkedin.com/in/huzaifa-jawed-030ab7275/)
