import os, httpx

EXPO_URL = "https://exp.host/--/api/v2/push/send"

async def send_expo_push(token: str, title: str, body: str):
    payload = {"to": token, "title": title, "body": body}
    async with httpx.AsyncClient(timeout=15) as cx:
        r = await cx.post(EXPO_URL, json=payload)
        return r.json()
