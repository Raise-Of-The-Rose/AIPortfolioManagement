from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models, database, auth, market_data
from datetime import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
CHAT_MODEL_ID = "HuggingFaceH4/zephyr-7b-beta:featherless-ai"

openai_client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
) if HF_TOKEN else None

router = APIRouter(prefix="/trade", tags=["trade"])

class TradeRequest(BaseModel):
    symbol: str
    quantity: int
    action: str # "BUY" or "SELL"

@router.post("/")
def execute_trade(trade: TradeRequest, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    symbol = trade.symbol.upper()
    current_price = market_data.get_current_price(symbol)
    
    if current_price is None:
        raise HTTPException(status_code=400, detail="Could not fetch current price for symbol")
    
    total_cost = current_price * trade.quantity

    if trade.action == "BUY":
        if current_user.balance < total_cost:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        
        # Deduct balance
        current_user.balance -= total_cost
        
        # Update or Create Holding
        holding = db.query(models.Holding).filter(
            models.Holding.user_id == current_user.id,
            models.Holding.symbol == symbol
        ).first()

        if holding:
            # Calculate new weighted average price
            total_value_existing = holding.quantity * holding.avg_price
            holding.quantity += trade.quantity
            holding.avg_price = (total_value_existing + total_cost) / holding.quantity
        else:
            new_holding = models.Holding(
                user_id=current_user.id,
                symbol=symbol,
                quantity=trade.quantity,
                avg_price=current_price
            )
            db.add(new_holding)

    elif trade.action == "SELL":
        holding = db.query(models.Holding).filter(
            models.Holding.user_id == current_user.id,
            models.Holding.symbol == symbol
        ).first()

        if not holding or holding.quantity < trade.quantity:
            raise HTTPException(status_code=400, detail="Insufficient holdings")
        
        # Add balance
        current_user.balance += total_cost
        
        # Update Holding
        holding.quantity -= trade.quantity
        if holding.quantity == 0:
            db.delete(holding)
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    # Record Transaction
    transaction = models.Transaction(
        user_id=current_user.id,
        symbol=symbol,
        transaction_type=trade.action,
        quantity=trade.quantity,
        price=current_price,
        timestamp=datetime.utcnow()
    )
    db.add(transaction)
    
    db.commit()
    
    return {"message": "Trade executed successfully", "balance": current_user.balance}

@router.get("/portfolio")
def get_portfolio(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    holdings = db.query(models.Holding).filter(models.Holding.user_id == current_user.id).all()
    results = []
    total_value = 0
    
    for h in holdings:
        current_price = market_data.get_current_price(h.symbol) or h.avg_price
        market_value = current_price * h.quantity
        unrealized_pnl = market_value - (h.avg_price * h.quantity)
        pnl_percent = (unrealized_pnl / (h.avg_price * h.quantity)) * 100 if h.quantity > 0 else 0
        
        results.append({
            "symbol": h.symbol,
            "quantity": h.quantity,
            "avg_price": h.avg_price,
            "current_price": current_price,
            "market_value": market_value,
            "unrealized_pnl": unrealized_pnl,
            "pnl_percent": pnl_percent
        })
        total_value += market_value
        
    return {
        "balance": current_user.balance,
        "portfolio_value": total_value,
        "total_equity": current_user.balance + total_value,
        "holdings": results
    }


@router.get("/analyze-buy/{symbol}")
def analyze_buy(
    symbol: str,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """AI-powered pre-trade analysis for a BUY action."""
    symbol = symbol.upper()

    if not openai_client:
        return {"analysis": "AI Offline: Please set HF_TOKEN environment variable."}

    current_price = market_data.get_current_price(symbol)
    price_str = f"${current_price:.2f}" if current_price else "unknown"

    # Get portfolio context
    holdings = db.query(models.Holding).filter(models.Holding.user_id == current_user.id).all()
    holdings_txt = ", ".join([f"{h.symbol}({h.quantity}@${h.avg_price:.2f})" for h in holdings]) or "none"

    prompt = (
        f"A user wants to BUY {symbol} at {price_str}. "
        f"Their balance is ${current_user.balance:.2f} and current holdings are: {holdings_txt}. "
        f"Give a concise 2-3 sentence recommendation: should they buy, hold off, or be cautious? "
        f"Consider diversification and risk. Be direct and practical."
    )

    try:
        completion = openai_client.chat.completions.create(
            model=CHAT_MODEL_ID,
            messages=[
                {"role": "system", "content": "You are a concise financial advisor. Give brief, practical advice."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=120,
            temperature=0.6,
        )
        analysis = completion.choices[0].message.content
        return {"analysis": analysis}
    except Exception as e:
        return {"analysis": f"AI analysis unavailable: {str(e)[:100]}"}
