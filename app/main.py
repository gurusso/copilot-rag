import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from app.rag import process_pdf, ask_copilot

app = FastAPI(
    title="Document Copilot API",
    description="API para ingestão de documentos e RAG com Gemini e ChromaDB",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    question: str

@app.post("/upload", status_code=201)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos.")
    
    content = await file.read()
    chunks_created = process_pdf(content, file.filename)
    
    return {
        "filename": file.filename,
        "status": "sucesso",
        "chunks_indexed": chunks_created
    }

@app.post("/chat")
async def chat_with_docs(payload: QueryRequest):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="A pergunta não pode estar vazia.")
    
    return ask_copilot(payload.question)