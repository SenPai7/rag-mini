from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    llm_provider: str = os.getenv("LLM_PROVIDER", "ollama").lower()
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1")
    embed_model: str = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

settings = Settings()
print(">>> SETTINGS:", settings.model_dump())

