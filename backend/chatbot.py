from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models, database, auth, market_data, trading

from openai import OpenAI
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/chat", tags=["chat"])

# --- LLM Setup ---
HF_TOKEN = os.getenv("HF_TOKEN")

# Chat Model via HuggingFace OpenAI-compatible router
CHAT_MODEL_ID = "HuggingFaceH4/zephyr-7b-beta:featherless-ai"

# Sentiment Model (Classification) — still uses InferenceClient
SENTIMENT_MODEL_ID = "ProsusAI/finbert"

# OpenAI-compatible client pointing at HuggingFace's router
openai_client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
) if HF_TOKEN else None

# InferenceClient for classification tasks (FinBERT)
try:
    hf_client = InferenceClient(token=HF_TOKEN)
except Exception:
    hf_client = None


def get_sentiment(text: str):
    if not hf_client:
        return None
    try:
        res = hf_client.text_classification(text, model=SENTIMENT_MODEL_ID)
        if isinstance(res, list) and len(res) > 0:
            top = max(res, key=lambda x: x.get('score', 0))
            return f"{top['label']} ({top['score']:.2f})"
        return str(res)
    except Exception as e:
        return f"Error: {e}"


class ChatRequest(BaseModel):
    message: str


@router.post("/")
def chat_with_bot(request: ChatRequest, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    if not openai_client:
        return {"response": "AI Offline: Please set HF_TOKEN environment variable."}

    # Build context from user's portfolio
    portfolio = trading.get_portfolio(current_user, db)
    holdings_txt = ", ".join([f"{h['symbol']}:{h['quantity']}" for h in portfolio['holdings']])

    messages = [
        {"role": "system", "content": f"You are a financial assistant. User Balance: ${portfolio['balance']:.2f}. Holdings: {holdings_txt}. Answer briefly."},
        {"role": "user", "content": request.message}
    ]

    try:
        # Optional FinBERT sentiment on explicit requests
        extra_info = ""
        if "sentiment" in request.message.lower() or "analyze" in request.message.lower():
            s = get_sentiment(request.message)
            if s:
                extra_info = f"\n(Sentiment Analysis of your query: {s})"

        completion = openai_client.chat.completions.create(
            model=CHAT_MODEL_ID,
            messages=messages,
            max_tokens=150,
            temperature=0.7,
        )
        return {"response": completion.choices[0].message.content + extra_info}
    except Exception as e:
        return {"response": f"AI Error: {str(e)}"}
