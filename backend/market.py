from fastapi import APIRouter, HTTPException
from typing import Optional
import market_data

router = APIRouter(prefix="/market", tags=["market"])

@router.get("/status")
def get_status():
    return market_data.get_market_status()

@router.get("/search")
def search_market(query: str):
    results = market_data.search_symbols(query)
    return results

@router.get("/quote/{symbol}")
def get_quote(symbol: str):
    data = market_data.get_quote(symbol)
    if not data:
        raise HTTPException(status_code=404, detail="Symbol not found")
    return data

@router.get("/info/{symbol}")
def get_stock_info(symbol: str):
    data = market_data.get_stock_info(symbol)
    if not data:
        raise HTTPException(status_code=404, detail="Stock not found")
    return data

@router.get("/history/{symbol}")
def get_stock_history(symbol: str, period: Optional[str] = "1mo"):
    data = market_data.get_stock_history(symbol, period)
    if not data:
        raise HTTPException(status_code=404, detail="History not found for symbol")
    return data
