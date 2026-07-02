import { useState, useEffect } from 'react'
import { getOrders, updateOrderStatus, getUsers } from '../api'
import type { Order } from '../api'
import { getUserId } from '../auth'

type Props = {
  onLogout: () => void
}

const STATUS_OPTIONS = ['Placed', 'In Transit', 'Delivered', 'Cancelled']

export default function DriverView({ onLogout }: Props) {
  const [orders, setOrders] = useState<Order[]>([])
  const [name, setName] = useState('')
  const myId = getUserId()

  useEffect(() => {
    getOrders().then(all => {
      setOrders(all.filter(o => o.driver_id === myId))
    })
    getUsers().then(all => {
      const me = all.find(u => u.id === myId)
      if (me) setName(me.name)
    })
  }, [])

  async function handleStatusChange(orderId: number, status: string) {
    try {
      await updateOrderStatus(orderId, status)
    } catch {
      return
    }
    const updated = orders.map(o => {
      if (o.id === orderId) return { ...o, status }
      return o
    })
    setOrders(updated)
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-2xl mx-auto p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">My Deliveries</h1>
          <button onClick={onLogout} className="text-sm text-gray-500 hover:text-gray-700">
            Log out
          </button>
        </div>

        {name && <p className="text-gray-600 mb-4">Welcome, {name}! Here are your assigned deliveries.</p>}

        {orders.length === 0 && <p className="text-gray-500">No orders assigned to you yet.</p>}

        <div className="space-y-3">
          {orders.map(order => (
            <div key={order.id} className="bg-white rounded-lg p-4 shadow-sm">
              <p className="font-medium">{order.description}</p>
              <div className="flex items-center gap-3 mt-2">
                <span className="text-sm text-gray-500">Status:</span>
                <select
                  value={order.status}
                  onChange={e => handleStatusChange(order.id, e.target.value)}
                  className="border rounded px-2 py-1 text-sm"
                >
                  {STATUS_OPTIONS.map(s => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
