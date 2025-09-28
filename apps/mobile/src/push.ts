import * as Notifications from 'expo-notifications';

export async function registerForPush(apiBase: string, userId: string) {
  const settings = await Notifications.getPermissionsAsync();
  let granted = settings.granted;
  if (!granted) {
    const req = await Notifications.requestPermissionsAsync();
    granted = req.granted;
  }
  if (!granted) return null;
  const token = (await Notifications.getExpoPushTokenAsync()).data;
  await fetch(`${apiBase}/devices`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ userId, token, kind: 'expo' })
  });
  return token;
}
