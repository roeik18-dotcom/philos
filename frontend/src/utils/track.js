const API_URL = process.env.REACT_APP_BACKEND_URL;

export function track(event, userId, metadata) {
  fetch(`${API_URL}/api/analytics/track`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ event, user_id: userId || 'anonymous', metadata }),
  }).catch(() => {});
}
