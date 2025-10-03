from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .rag_chain import answer

app = FastAPI(title="RAG Mini", version="0.1.0")

class AskReq(BaseModel):
    question: str
    k: int | None = 4

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(req: AskReq):
    try:
        return answer(req.question, k=req.k or 4)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
