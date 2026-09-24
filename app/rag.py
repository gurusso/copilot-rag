import os
import io
import chromadb
from google import genai
from pypdf import PdfReader
from dotenv import load_dotenv

# 1. Carrega as variáveis de ambiente no início
load_dotenv()

# 2. Inicialização dos clientes
chroma_client = chromadb.PersistentClient(path="./data/chroma")
collection = chroma_client.get_or_create_collection(name="documentos")
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def process_pdf(file_bytes: bytes, filename: str) -> int:
    """Extrai texto do PDF, divide em blocos e salva no ChromaDB com Embeddings."""
    pdf = PdfReader(io.BytesIO(file_bytes))
    
    full_text = ""
    for page in pdf.pages:
        extracted = page.extract_text()
        if extracted:
            full_text += extracted + "\n"

    if not full_text.strip():
        return 0

    chunk_size = 800
    overlap = 100
    text_chunks = []
    
    i = 0
    while i < len(full_text):
        chunk = full_text[i : i + chunk_size]
        text_chunks.append(chunk)
        i += chunk_size - overlap if (chunk_size - overlap) > 0 else chunk_size

    documents, ids, embeddings = [], [], []
    for idx, chunk in enumerate(text_chunks):
        response = gemini_client.models.embed_content(
            model="models/gemini-embedding-001",
            contents=chunk,
        )
        embedding_values = response.embeddings[0].values
        
        documents.append(chunk)
        ids.append(f"{filename}_chunk_{idx}")
        embeddings.append(embedding_values)

    if documents:
        collection.add(
            documents=documents,
            embeddings=embeddings,
            ids=ids
        )
        
    return len(documents)


def ask_copilot(question: str) -> dict:
    """Gera embedding da pergunta, busca no banco vetorial e gera a resposta."""
    q_response = gemini_client.models.embed_content(
        model="models/gemini-embedding-001",
        contents=question,
    )
    q_embedding_values = q_response.embeddings[0].values
    
    results = collection.query(
        query_embeddings=[q_embedding_values],
        n_results=3
    )
    
    context_chunks = results["documents"][0] if results and results.get("documents") and results["documents"][0] else []
    context = "\n---\n".join(context_chunks) if context_chunks else "Nenhum contexto relevante encontrado."

    prompt = f"""
    Você é um copiloto especialista em análise de documentos. 
    Responda à pergunta do usuário utilizando EXCLUSIVAMENTE o contexto fornecido abaixo.
    Se a resposta não estiver no contexto, responda: "Não encontrei essa informação no documento fornecido."

    Contexto do Documento:
    {context}

    Pergunta do Usuário:
    {question}
    """

    response = gemini_client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt
    )

    return {
        "answer": response.text,
        "sources": context_chunks
    }