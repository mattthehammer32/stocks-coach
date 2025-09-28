import os, re, math
from typing import Dict

# Optional: OpenAI-compatible client
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE = os.getenv("OPENAI_BASE")  # e.g., https://api.openai.com/v1 or your Azure/OpenRouter base
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def _heuristic_impact(text: str):
    t = text.lower()
    bullish_kw = ["beats", "beat", "record revenue", "raises guidance", "upgrade", "acquisition", "buyback", "profit", "strong demand"]
    bearish_kw = ["misses", "miss", "cut guidance", "downgrade", "probe", "investigation", "recall", "lawsuit", "layoffs", "weak demand", "loss"]
    score = 0
    for w in bullish_kw:
        if w in t: score += 1
    for w in bearish_kw:
        if w in t: score -= 1
    if score > 0: return "bullish", min(0.6 + 0.1*score, 0.95)
    if score < 0: return "bearish", min(0.6 + 0.1*(-score), 0.95)
    return "neutral", 0.35

def summarize_article(title: str, body: str, ticker: str) -> Dict:
    """Return {summary, impact, confidence, reasons[]}.If OPENAI_API_KEY is set, uses LLM. Otherwise uses a heuristic fallback.    """
    text = (title or "") + "\n\n" + (body or "")
    if OPENAI_KEY and OPENAI_BASE:
        try:
            import httpx
            system = "You are a finance news analyst. Summarize in <=60 words. Decide impact (bullish, bearish, neutral) for near-term price moves and give confidence (0-1) with 1-2 short reasons."
            user = f"Ticker: {ticker}\nTitle: {title}\nBody: {body[:6000]}"
            payload = {
                "model": OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                "temperature": 0.2,
                "max_tokens": 200
            }
            headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
            with httpx.Client(base_url=OPENAI_BASE, timeout=30) as cx:
                r = cx.post("/chat/completions", json=payload, headers=headers)
                r.raise_for_status()
                out = r.json()
                content = out.get("choices",[{}])[0].get("message",{}).get("content","").strip()
                # Expect a short paragraph; parse simple tags if present
                impact, confidence = _heuristic_impact(content)
                return {
                    "summary": content[:500],
                    "impact": impact,
                    "confidence": confidence,
                    "reasons": []
                }
        except Exception as e:
            # fall through to heuristic
            pass
    impact, conf = _heuristic_impact(text)
    # naive summary
    s = (body or title or "").strip()
    if len(s) > 260: s = s[:257] + "..."
    if not s: s = "Headline noted; details insufficient for a confident assessment."
    return {"summary": s, "impact": impact, "confidence": conf, "reasons": []}
