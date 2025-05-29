from fastapi import APIRouter, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import faiss
import numpy as np
from pydantic import BaseModel
from app.rag.retriever import retriever
from app.db.models import Chunk
from app.rag.llm import generate_answer
from app.db.models import QueryLog

from app.db.base import get_db
from app.db.models import Document
from app.rag.embedding import embedder_singleton
from app.rag.pptx_parser import parse_pptx
from app.core.config import get_settings

router = APIRouter()

UPLOAD_DIR = "storage/docs"
INDEX_PATH = get_settings().FAISS_INDEX_PATH
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)

class QueryRequest(BaseModel):
    question: str
    top_k: int = 3

class QueryResponse(BaseModel):
    answer: str
    context: list[str]

@router.post("/upload")
async def upload_pptx(file: UploadFile, course_id: str, db: Session = Depends(get_db)):
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    texts = parse_pptx(filepath)
    if not texts:
        raise HTTPException(status_code=400, detail="No text found in PPTX")

    embeddings = embedder_singleton.embed(texts)
    dimension = embeddings[0].shape[0]

    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
    else:
        index = faiss.IndexFlatL2(dimension)

    index.add(np.array(embeddings))
    faiss.write_index(index, INDEX_PATH)

    document = Document(
        filename=file.filename,
        course_id=course_id,
        filepath=filepath,
        num_chunks=len(embeddings),
    )
    db.add(document)
    db.commit()
    db.refresh(document) 
    
    # Store chunks
    for idx, text in enumerate(texts):
        db.add(Chunk(
            document_id=document.id,
            chunk_index=idx,
            text=text
        ))
    db.commit()
    db.refresh(document)
    return {"id": document.id, "message": "Uploaded, parsed, and embedded."}


@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        context = retriever.query(request.question, request.top_k)
        answer = generate_answer(request.question, context)

        db.add(QueryLog(question=request.question, answer=answer))
        db.commit()

        return QueryResponse(answer=answer, context=context)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
