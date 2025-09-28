
# Stocks Coach (Monorepo)
Clean, real-time entry/exit coach with Lightweight Charts and a FastAPI backend.

## What’s inside
- **apps/web** – Next.js + Lightweight Charts (candles, SMA(52), 52-week bands, swing pins, entry/exit markers)
- **apps/api** – FastAPI that serves `/history/:symbol` and a demo websocket at `/stream/:symbol`
- **packages/shared** – place for shared types/schemas later
- **infra** – dev Docker compose (optional), Railway/Vercel notes

## Quick start (local)
1) Install prerequisites: Node 20+, Python 3.11+
2) From repo root, install JS deps:
   ```bash
   npm i -g pnpm
   pnpm i
   ```
3) Install API deps:
   ```bash
   pip install -r apps/api/requirements.txt
   ```
4) Set env for the web app (create `apps/web/.env.local`):
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
5) Run both (web + api) in split terminals:
   ```bash
   # Terminal A
   uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
   # Terminal B
   pnpm --filter @stocks/web dev
   ```
   Visit http://localhost:3000

### Commands (monorepo helpers)
- `pnpm dev:web` – start Next.js
- `pnpm dev:api` – start FastAPI (requires `pip install -r apps/api/requirements.txt`)

## Deploy (recommended)
### Web (Next.js) → Vercel
- Push this repo to GitHub
- Import to Vercel → Framework: Next.js → Root dir: `apps/web`
- Add env var `NEXT_PUBLIC_API_URL` = your API URL (from Railway/Fly)
- Deploy

### API (FastAPI) → Railway
- New Project → Deploy from GitHub → Set root to `apps/api` (Dockerfile provided)
- Add env vars (none required for demo; add vendor keys later)
- Railway gives you a public URL like `https://<app>.up.railway.app`

Update `NEXT_PUBLIC_API_URL` in Vercel to point to the Railway URL.

## Notes
- Data uses `yfinance` (EOD/delayed). For realtime, wire your vendor’s websocket to `/stream/:symbol`.
- This project is **education/research** only. Not financial advice.


---

## Mobile + Push + News (added)

### Mobile (Expo)
1) `cd apps && npx create-expo-app@latest mobile --template blank`
2) `cd mobile && npm i expo-notifications`
3) Copy `apps/mobile/src/push.ts` and `apps/mobile/App.js` into your Expo project.
4) Add `EXPO_PUBLIC_API_URL` in `app.json` or `.env` to point to your API (Railway URL).

### API
- New endpoints:
  - `POST /devices` to register push tokens
  - `POST /alerts` / `GET /alerts` to manage alerts (in-memory for now)
  - `GET /news/:symbol` and `GET /news/fetch/:symbol` (stub feed + cache)

### Worker
- `apps/worker/main.py` polls `/news/fetch/:symbol` every 2 minutes. Run with:
  ```bash
  pip install -r apps/worker/requirements.txt
  python apps/worker/main.py
  ```

### Web
- `NewsPanel` renders an AI Take + list of news under the chart.

> Replace the news stub with a real provider (Polygon/NewsAPI) and connect an LLM to score impact.
