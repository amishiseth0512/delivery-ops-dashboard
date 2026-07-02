import { getToken } from './auth'

const BASE = 'http://localhost:8000'

export type Order = {
  id: number
  description: string
  status: string
  driver_id: number | null
  created_at: string
}

export type User = {
  id: number
  name: string
  email: string
  role: string
}

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${getToken()}`,
  }
}

export async function login(email: string, password: string) {
  const res = await fetch(`${BASE}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  if (!res.ok) throw new Error('Incorrect email or password')
  return res.json() as Promise<{ access_token: string; token_type: string }>
}

export async function getOrders(): Promise<Order[]> {
  const res = await fetch(`${BASE}/orders/`, { headers: authHeaders() })
  return res.json()
}

export async function getUsers(): Promise<User[]> {
  const res = await fetch(`${BASE}/users/`, { headers: authHeaders() })
  return res.json()
}

export async function reassignOrder(orderId: number, driverId: number) {
  const res = await fetch(`${BASE}/orders/${orderId}/reassign`, {
    method: 'PATCH',
    headers: authHeaders(),
    body: JSON.stringify({ driver_id: driverId }),
  })
  if (!res.ok) throw new Error('Failed to reassign order')
  return res.json()
}

export async function updateOrderStatus(orderId: number, status: string) {
  const res = await fetch(`${BASE}/orders/${orderId}/status`, {
    method: 'PATCH',
    headers: authHeaders(),
    body: JSON.stringify({ status }),
  })
  if (!res.ok) throw new Error('Failed to update status')
  return res.json()
}
