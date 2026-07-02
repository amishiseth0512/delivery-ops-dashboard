export function saveToken(token: string) {
  localStorage.setItem('token', token)
}

export function getToken(): string | null {
  return localStorage.getItem('token')
}

export function clearToken() {
  localStorage.removeItem('token')
}

export function getRole(): string | null {
  const token = getToken()
  if (!token) return null
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.role
  } catch {
    return null
  }
}

export function getUserId(): number | null {
  const token = getToken()
  if (!token) return null
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return parseInt(payload.sub)
  } catch {
    return null
  }
}
