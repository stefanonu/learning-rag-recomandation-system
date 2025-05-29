import faiss
import numpy as np
from app.rag.embedding import embedder_singleton
from app.core.config import get_settings
from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.db.models import Chunk
import os


settings = get_settings()

class RAGRetriever:
    def __init__(self):
        self.index_path = settings.FAISS_INDEX_PATH
        if not os.path.exists(self.index_path):
            raise FileNotFoundError(f"FAISS index not found at {self.index_path}")
        self.index = faiss.read_index(self.index_path)

    def query(self, question: str, top_k: int = 3):
        embedding = embedder_singleton.embed([question])
        distances, indices = self.index.search(np.array(embedding), top_k)
        idxs = indices[0].tolist()

        with SessionLocal() as db:
            chunks = db.query(Chunk).filter(Chunk.chunk_index.in_(idxs)).all()
            return [chunk.text for chunk in chunks]

retriever = RAGRetriever()
