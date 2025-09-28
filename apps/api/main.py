
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
import pandas as pd, numpy as np, yfinance as yf
import asyncio, json
from apps.api.news import fetch_polygon_news

app = FastAPI(title="Stocks Coach API")

def compute(symbol="AAPL", period="2y", interval="1d"):
    df = yf.download(symbol, period=period, interval=interval, auto_adjust=True, progress=False)
    df = df.rename(columns=str.title)  # Open/High/Low/Close
    # Indicators
    df["SMA52"] = df["Close"].rolling(52).mean()
    tr = pd.concat([(df["High"]-df["Low"]),
                    (df["High"]-df["Close"].shift()).abs(),
                    (df["Low"]-df["Close"].shift()).abs()], axis=1).max(axis=1)
    df["ATR14"] = tr.rolling(14).mean()
    df["Vol5"] = df["Volume"].rolling(5).mean()
    df["Vol20"] = df["Volume"].rolling(20).mean()
    df["VolBoost"] = df["Vol5"] / df["Vol20"]
    df["H52"] = df["High"].rolling(252).max()
    df["L52"] = df["Low"].rolling(252).min()

    # Swing highs/lows (k=2)
    k = 2
    df["SwingHigh"] = (df["High"] == df["High"].rolling(1+k+k, center=True).max())
    df["SwingLow"]  = (df["Low"]  == df["Low"].rolling(1+k+k,  center=True).min())

    # Signals
    prev_below = df["Close"].shift() < df["SMA52"].shift()
    entry = (df["Close"] > df["SMA52"]) & prev_below & (df["VolBoost"] >= 1.3)
    exit_sma = df["Close"] < df["SMA52"]

    # Build signal list
    sig = []
    for ts, r in df.iterrows():
        if pd.notna(r.get("SMA52")) and pd.notna(r.get("ATR14")):
            if bool(entry.get(ts, False)):
                sig.append({"time": int(ts.timestamp()), "kind": "ENTRY",
                            "why": ["Close crossed above SMA(52)", f"Vol thrust {r['VolBoost']:.2f} ≥ 1.3"]})
            elif bool(exit_sma.get(ts, False)):
                sig.append({"time": int(ts.timestamp()), "kind": "EXIT",
                            "why": ["Close fell below SMA(52)"]})

    df = df.dropna(subset=["SMA52","ATR14"])
    return df, sig

class HistoryOut(BaseModel):
    timestamps: list[int]
    open: list[float]; high: list[float]; low: list[float]; close: list[float]; volume: list[int]
    sma52: list[float]; atr14: list[float]; h52: list[float]; l52: list[float]
    swing_high_idx: list[int]; swing_low_idx: list[int]
    signals: list[dict]

@app.get("/healthz")
def healthz(): return {"ok": True}

@app.get("/history/{symbol}", response_model=HistoryOut)
def history(symbol: str, period: str="2y", interval: str="1d"):
    df, sig = compute(symbol, period, interval)
    ts = [int(x.timestamp()*1000) for x in df.index]  # ms
    sh_idx = [i for i, v in enumerate(df["SwingHigh"].tolist()) if bool(v)]
    sl_idx = [i for i, v in enumerate(df["SwingLow"].tolist())  if bool(v)]
    return {
        "timestamps": ts,
        "open": df["Open"].round(2).tolist(),
        "high": df["High"].round(2).tolist(),
        "low":  df["Low"].round(2).tolist(),
        "close":df["Close"].round(2).tolist(),
        "volume": df["Volume"].astype(int).tolist(),
        "sma52": df["SMA52"].round(2).tolist(),
        "atr14": df["ATR14"].round(2).tolist(),
        "h52": df["H52"].round(2).tolist(),
        "l52": df["L52"].round(2).tolist(),
        "swing_high_idx": sh_idx,
        "swing_low_idx": sl_idx,
        "signals": sig
    }

@app.websocket("/stream/{symbol}")
async def stream(ws: WebSocket, symbol: str):
    await ws.accept()
    # Demo: emit the last historical bar once, then heartbeat (replace with real vendor stream)
    df, _ = compute(symbol, "6mo", "1d")
    if len(df):
        ts = df.index[-1]
        r = df.iloc[-1]
        msg = {"t": int(ts.timestamp()), "o": float(r.Open), "h": float(r.High), "l": float(r.Low), "c": float(r.Close), "v": int(r.Volume)}
        await ws.send_text(json.dumps({"bar": msg}))
    while True:
        await asyncio.sleep(1.0)
        await ws.send_text(json.dumps({"ping": True}))

# --- Simple in-memory stores (replace with DB later) ---
DEVICES = []  # {userId, token, kind}
ALERTS  = []  # {id, userId, symbol, rule, channels, active}
NEWS_CACHE = {}  # { symbol: [ {title,url,published_at,summary,impact,confidence,source} ] }

@app.post("/devices")
def register_device(payload: dict):
    # payload: {userId, token, kind: 'expo'|'web'|'sms'}
    if not payload.get("token"):
        return {"ok": False, "error": "missing token"}
    DEVICES.append({"userId": payload.get("userId"), "token": payload["token"], "kind": payload.get("kind","expo")})
    return {"ok": True, "count": len(DEVICES)}

@app.get("/devices")
def list_devices(): return {"devices": DEVICES}

@app.post("/alerts")
def create_alert(payload: dict):
    payload["id"] = len(ALERTS)+1
    payload.setdefault("active", True)
    ALERTS.append(payload)
    return {"ok": True, "alert": payload}

@app.get("/alerts")
def list_alerts(userId: str | None = None):
    items = ALERTS if not userId else [a for a in ALERTS if a.get("userId")==userId]
    return {"alerts": items}

# --- News endpoints (provider-agnostic stubs) ---
@app.get("/news/{symbol}")
def news(symbol: str, limit: int = 15):
    items = NEWS_CACHE.get(symbol.upper(), [])
    return items[:limit]

@app.get("/news/fetch/{symbol}")
def news_fetch(symbol: str, limit: int = 20):
    sym = symbol.upper()
    # Pull from Polygon; if no key configured, keep existing cache
    try:
        fetched = fetch_polygon_news(sym, limit=limit)
        if fetched:
            # Dedup by URL; newest first
            seen = set()
            merged = []
            for it in fetched + NEWS_CACHE.get(sym, []):
                k = it.get("url")
                if k and k not in seen:
                    seen.add(k)
                    merged.append(it)
            NEWS_CACHE[sym] = merged[:50]
    except Exception as e:
        # Keep old cache on failure
        pass
    return {"ok": True, "count": len(NEWS_CACHE.get(sym, []))}
