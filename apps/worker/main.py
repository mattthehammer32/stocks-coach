import asyncio, os, json, time, httpx
from datetime import datetime, timezone

API = os.getenv("API_URL", "http://localhost:8000")
SYMBOLS = [s.strip() for s in os.getenv("SYMBOLS","AAPL,MSFT,NVDA").split(",")]

async def poll_news(symbol="AAPL"):
    async with httpx.AsyncClient(timeout=20) as cx:
        # This will trigger server-side fetch/caching; replace with your provider in the API
        r = await cx.get(f"{API}/news/fetch/{symbol}")
        r.raise_for_status()
        print("polled news", symbol, r.json())
        return r.json()

async def loop():
    while True:
        for s in SYMBOLS:
            try:
                await poll_news(s)
            except Exception as e:
                print("news error", s, e)
        await asyncio.sleep(120)

if __name__ == "__main__":
    asyncio.run(loop())
