import os, time, math
from typing import Dict, List
import httpx
from summarizer import summarize_article

POLYGON_KEY = os.getenv("POLYGON_KEY")
POLYGON_BASE = os.getenv("POLYGON_BASE", "https://api.polygon.io")

def fetch_polygon_news(symbol: str, limit: int = 20) -> List[Dict]:
    if not POLYGON_KEY:
        # No key — return empty (the API layer can handle stubbing)
        return []
    params = {
        "ticker": symbol.upper(),
        "limit": limit,
        "order": "desc",
        "sort": "published_utc",
        "apiKey": POLYGON_KEY
    }
    with httpx.Client(timeout=20) as cx:
        r = cx.get(f"{POLYGON_BASE}/v2/reference/news", params=params)
        r.raise_for_status()
        data = r.json()
        results = data.get("results", [])
    items = []
    for x in results:
        title = x.get("title","")
        desc = x.get("description","") or ""
        url = x.get("article_url") or x.get("url")
        published = x.get("published_utc")
        source = (x.get("publisher") or {}).get("name") or "polygon"
        # Summarize
        take = summarize_article(title, desc, symbol)
        items.append({
            "title": title,
            "url": url,
            "published_at": published,
            "source": source,
            "summary": take["summary"],
            "impact": take["impact"],
            "confidence": take["confidence"]
        })
    return items
