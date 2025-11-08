from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def chunk_text(text, max_length=500):
  words = text.split()
  chunks = []
  current = []
  count = 0
  for w in words:
    current.append(w)
    count+=1
    if count >= max_length:
      chunks.append(" ".join(current))
      current = []
      count = 0
  if current:
    chunks.append(" ".join(current))
  return chunks

def build_vector_store(text):
    chunks = chunk_text(text)
    embeddings = model.encode(chunks)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype('float32'))
    return chunks, index

def get_context(question, session, top_k=3):
    question_embedding = model.encode([question])
    D, I = session['index'].search(np.array(question_embedding).astype('float32'), top_k)
    return [session['chunks'][i] for i in I[0]]