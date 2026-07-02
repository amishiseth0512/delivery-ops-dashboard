import { useState, useEffect } from 'react'
import { getOrders, getUsers, reassignOrder } from '../api'
import type { Order, User } from '../api'
import ReassignModal from '../components/ReassignModal'
import { getUserId } from '../auth'

type Props = {
  onLogout: () => void
}

export default function Dashboard({ onLogout }: Props) {
  const [orders, setOrders] = useState<Order[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [reassigning, setReassigning] = useState<number | null>(null)

  useEffect(() => {
    getOrders().then(setOrders)
    getUsers().then(setUsers)
  }, [])

  const drivers = users.filter(u => u.role === 'driver')
  const myName = users.find(u => u.id === getUserId())?.name ?? ''

  function driverName(id: number | null) {
    if (!id) return 'Unassigned'
    const found = users.find(u => u.id === id)
    return found ? found.name : 'Unknown'
  }

  async function handleReassign(orderId: number, driverId: number) {
    await reassignOrder(orderId, driverId)
    const updated = await getOrders()
    setOrders(updated)
    setReassigning(null)
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-4xl mx-auto p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">Dispatcher Dashboard</h1>
          <button onClick={onLogout} className="text-sm text-gray-500 hover:text-gray-700">
            Log out
          </button>
        </div>

        {myName && <p className="text-gray-600 mb-4">Welcome, {myName}! Here's an overview of all orders.</p>}

        {orders.length === 0 && <p className="text-gray-500">No orders yet.</p>}

        <div className="space-y-3">
          {orders.map(order => (
            <div key={order.id} className="bg-white rounded-lg p-4 shadow-sm">
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-medium">{order.description}</p>
                  <p className="text-sm text-gray-500 mt-1">
                    Status: {order.status} · Driver: {driverName(order.driver_id)}
                  </p>
                </div>
                <button
                  onClick={() => setReassigning(reassigning === order.id ? null : order.id)}
                  className="text-sm text-blue-600 hover:underline ml-4 shrink-0"
                >
                  Reassign
                </button>
              </div>

              {reassigning === order.id && (
                <ReassignModal
                  drivers={drivers}
                  onConfirm={driverId => handleReassign(order.id, driverId)}
                  onCancel={() => setReassigning(null)}
                />
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
