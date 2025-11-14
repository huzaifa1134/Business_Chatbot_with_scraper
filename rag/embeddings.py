# rag/embeddings.py
# from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import hashlib

# model = SentenceTransformer('all-MiniLM-L6-v2')

def chunk_text(text, max_length=400):
    words = text.split()
    chunks = []
    current = []
    count = 0
    for w in words:
        current.append(w)
        count += 1
        if count >= max_length:
            chunks.append(" ".join(current))
            current = []
            count = 0
    if current:
        chunks.append(" ".join(current))
    return chunks

def embed_text(text):
    """
    Simple deterministic embedding for a chunk.
    Converts text into a normalized float32 vector.
    """
    h = int(hashlib.sha256(text.encode('utf-8')).hexdigest(), 16)
    vec = np.array([(h >> i) & 0xFF for i in range(0, 384)], dtype='float32')
    vec = vec / np.linalg.norm(vec)
    return vec 

def build_vector_store(text):
    """Return chunks and FAISS index"""
    chunks = chunk_text(text)
    embeddings = np.array([embed_text(c) for c in chunks], dtype='float32')
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return chunks, index

def get_context(question, session, top_k=3):
    """Return top k relevant chunks from FAISS index"""
    question_embedding = np.array([embed_text(question)], dtype='float32')
    D, I = session['index'].search(question_embedding, top_k)
    return [session['chunks'][i] for i in I[0]]
