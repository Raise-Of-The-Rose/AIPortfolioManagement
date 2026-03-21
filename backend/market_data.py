import yfinance as yf
from datetime import datetime
import pytz

# In-memory cache
price_cache = {}

def get_market_status():
    """
    Checks if NYSE is open. 
    Simplification: Mon-Fri 9:30 AM - 4:00 PM ET, excluding holidays (not strictly handled here).
    """
    ny_tz = pytz.timezone('America/New_York')
    now = datetime.now(ny_tz)
    
    # Check Weekend
    if now.weekday() >= 5: # 5=Sat, 6=Sun
        return {"status": "CLOSED", "reason": "Weekend"}

    # Check Time
    start = now.replace(hour=9, minute=30, second=0, microsecond=0)
    end = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    if start <= now <= end:
         return {"status": "OPEN", "reason": "Market Open"}
    else:
         return {"status": "CLOSED", "reason": "After Hours"}

def fetch_price(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        # fast_info is reliable for real-time
        price = ticker.fast_info.last_price
        # Also get change % if possible, though fast_info might split it
        return price
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        return None

def get_quote(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        return {
            "symbol": symbol.upper(),
            "price": info.last_price,
            "previous_close": info.previous_close,
            "change_percent": ((info.last_price - info.previous_close) / info.previous_close * 100) if info.previous_close else 0
        }
    except Exception:
        return None

def get_current_price(symbol: str):
    # Backward compatibility
    q = get_quote(symbol)
    return q['price'] if q else None

def get_stock_history(symbol: str, period="1mo"):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        if hist.empty:
            return []
        hist.reset_index(inplace=True)
        hist['Date'] = hist['Date'].dt.strftime('%Y-%m-%d')
        return hist[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].to_dict(orient="records")
    except Exception as e:
        print(f"Error fetching history for {symbol}: {e}")
        return []

def get_stock_info(symbol: str):
    """Fetch detailed company info for the StockDetail page."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        # Validate: yfinance returns a minimal dict for invalid symbols
        if not info or info.get('quoteType') is None:
            return None
        return {
            "symbol": symbol.upper(),
            "name": info.get("longName") or info.get("shortName", symbol.upper()),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "summary": info.get("longBusinessSummary", "No description available."),
            "marketCap": info.get("marketCap"),
            "volume": info.get("volume"),
            "averageVolume": info.get("averageVolume"),
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
            "trailingPE": info.get("trailingPE"),
            "dividendYield": info.get("dividendYield"),
        }
    except Exception as e:
        print(f"Error fetching info for {symbol}: {e}")
        return None

# Fallback symbol map for instant search results
KNOWN_SYMBOLS = {
    "AAPL": "Apple Inc.", "MSFT": "Microsoft Corp.", "GOOGL": "Alphabet Inc.",
    "AMZN": "Amazon.com Inc.", "TSLA": "Tesla Inc.", "NVDA": "NVIDIA Corp.",
    "META": "Meta Platforms Inc.", "NFLX": "Netflix Inc.", "AMD": "AMD Inc.",
    "INTC": "Intel Corp.", "DIS": "Walt Disney Co.", "KO": "Coca-Cola Co.",
    "PEP": "PepsiCo Inc.", "JNJ": "Johnson & Johnson", "PG": "Procter & Gamble",
    "BTC-USD": "Bitcoin USD", "BRK-B": "Berkshire Hathaway", "JPM": "JPMorgan Chase",
    "V": "Visa Inc.", "MA": "Mastercard Inc.", "WMT": "Walmart Inc.",
    "PYPL": "PayPal Holdings", "CRM": "Salesforce Inc.", "UBER": "Uber Technologies",
}

def search_symbols(query: str):
    """Search for stock symbols. Uses local map first, then yfinance.Search."""
    q_up = query.strip().upper()
    # Local fast match: symbol prefix or company name substring
    local = [
        {"symbol": sym, "shortname": name}
        for sym, name in KNOWN_SYMBOLS.items()
        if q_up in sym or q_up in name.upper()
    ]
    if local:
        return local[:7]
    # Fallback: yfinance Search (requires yfinance >= 0.2.28)
    try:
        from yfinance import Search
        results = Search(query, max_results=7)
        quotes = results.quotes or []
        return [
            {
                "symbol": q.get("symbol", ""),
                "shortname": q.get("shortname") or q.get("longname", ""),
            }
            for q in quotes
            if q.get("symbol")
        ]
    except Exception as e:
        print(f"Search fallback error: {e}")
        return []
