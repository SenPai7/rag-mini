# RAG Mini (LangChain + FAISS + FastAPI)

یک پروژه‌ی مینیمال برای پیاده‌سازی RAG سبک و تمیز. شما می‌توانید از **Ollama (لوکال)** یا **OpenAI** برای LLM استفاده کنید و از **FAISS** برای بردارها.

## 0) پیش‌نیازها
- Python 3.10+
- (اختیاری) نصب Ollama برای اجرای مدل LLM روی سیستم خود: https://ollama.com/
- (اختیاری) کلید OpenAI اگر بخواهید از OpenAI استفاده کنید.

## 1) نصب
```bash
python -m venv .venv
source .venv/bin/activate   # یا در ویندوز: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

در فایل `.env` مقدار `LLM_PROVIDER` را روی **ollama** یا **openai** بگذارید. اگر `openai` انتخاب کردید، `OPENAI_API_KEY` را ست کنید.

## 2) افزودن داده‌ها
فایل‌های متنی (`.txt`, `.md`) را داخل پوشه‌ی `data/` قرار دهید.

## 3) ایندکس‌سازی (Ingest)
```bash
python -m app.ingest data
```
این مرحله متن‌ها را chunk می‌کند، امبدینگ می‌سازد و در `storage/faiss_index/` ذخیره می‌کند.

## 4) اجرا
```bash
uvicorn app.main:app --reload
```
سپس:
```bash
curl -X POST "http://127.0.0.1:8000/ask" -H "Content-Type: application/json" -d '{"question":"What is this project about?"}'
```
یا در مرورگر: `http://127.0.0.1:8000/docs`

## 5) Docker (اختیاری)
```bash
docker build -t rag-mini:latest .
docker run -p 8000:8000 --env-file .env -v $(pwd)/data:/app/data -v $(pwd)/storage:/app/storage rag-mini:latest
```
> اگر از Ollama استفاده می‌کنید، باید سرویس Ollama روی سیستم‌تان فعال باشد.

## 6) مسیرهای بعدی
- اضافه‌کردن ارزیابی (RAGAS) و تست‌های ساده.
- جایگزین‌کردن FAISS با Weaviate/Qdrant (نیاز به تغییرات کوچک در کد).
- افزودن UI سبک (Streamlit/Gradio).
