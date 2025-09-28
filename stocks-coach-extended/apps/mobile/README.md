# Mobile (Expo) — Stocks Coach
Use Expo for iOS/Android. Fast push, OTA updates.

## Create the app (one-time)
```bash
cd apps
npx create-expo-app@latest mobile --template blank
cd mobile
npm i expo-notifications
```

Copy the files in this folder into your new `apps/mobile` project (merge `src/`).
Add this to `app.json`:
```json
{
  "expo": {
    "plugins": ["expo-notifications"],
    "android": { "useNextNotificationsApi": true }
  }
}
```

## Push registration
Edit `src/push.ts` with your API base URL, then call `registerForPush()` on startup.
