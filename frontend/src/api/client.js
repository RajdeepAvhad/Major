// Reads CSRF cookie set by Django
function getCookie(name) {
  const match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
  return match ? decodeURIComponent(match[1]) : null;
}

export async function apiGet(url) {
  const res = await fetch(url, { credentials: 'include' });
  return res.json();
}

export async function apiPost(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken') || '',
    },
    body: JSON.stringify(body),
  });
  return res.json();
}
