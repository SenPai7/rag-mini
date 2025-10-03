from __future__ import annotations

from pathlib import Path
from typing import List, Optional
import os
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.prompts import ChatPromptTemplate

from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

from .config import settings

STORAGE_DIR = Path(__file__).resolve().parent.parent / "storage" / "faiss_index"

def get_embeddings():
    return HuggingFaceEmbeddings(model_name=settings.embed_model)

def load_index() -> Optional[FAISS]:
    if STORAGE_DIR.exists():
        return FAISS.load_local(
            str(STORAGE_DIR),
            get_embeddings(),
            allow_dangerous_deserialization=True,
        )
    return None

def build_index(docs: List[Document]) -> FAISS:
    embeddings = get_embeddings()
    vs = FAISS.from_documents(docs, embeddings)
    STORAGE_DIR.parent.mkdir(parents=True, exist_ok=True)
    vs.save_local(str(STORAGE_DIR))
    return vs

def chunk_text(text: str, source: str) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700, chunk_overlap=120, separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_text(text)
    return [Document(page_content=c, metadata={"source": source}) for c in chunks]

def load_text_files(paths: List[Path]) -> List[Document]:
    docs: List[Document] = []
    for p in paths:
        if p.is_dir():
            for child in p.rglob("*.txt"):
                docs.extend(chunk_text(child.read_text(encoding="utf-8"), str(child)))
            for child in p.rglob("*.md"):
                docs.extend(chunk_text(child.read_text(encoding="utf-8"), str(child)))
        elif p.suffix.lower() in [".txt", ".md"]:
            docs.extend(chunk_text(p.read_text(encoding="utf-8"), str(p)))
    return docs

# def get_llm():
#     if settings.llm_provider == "openai":
#         if not settings.openai_api_key:
#             raise RuntimeError("OPENAI_API_KEY is not set but LLM_PROVIDER=openai")
#         return ChatOpenAI(model="gpt-4o-mini", temperature=0)
#     return ChatOllama(model=settings.ollama_model, temperature=0)

def get_llm():
    if settings.llm_provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o-mini", temperature=0)

    return ChatOllama(
        model=settings.ollama_model,
        base_url=os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434"),
        temperature=0,
    )

RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a concise assistant. Use the given context. If you don't know, say you don't know."),
    ("user", "Context:\n{context}\n\nQuestion: {question}\nAnswer in the same language as the question."),
])

def answer(question: str, k: int = 4) -> dict:
    index = load_index()
    if index is None:
        raise RuntimeError("No index found. Run ingestion first: `python -m app.ingest data`.")
    retriever = index.as_retriever(search_kwargs={"k": k})
    docs = retriever.invoke(question)
    context = "\n\n".join(d.page_content for d in docs)
    llm = get_llm()
    messages = RAG_PROMPT.format_messages(context=context, question=question)
    resp = llm.invoke(messages)
    content = getattr(resp, "content", str(resp))
    sources = [d.metadata.get("source") for d in docs]
    return {"answer": content, "sources": sources}
