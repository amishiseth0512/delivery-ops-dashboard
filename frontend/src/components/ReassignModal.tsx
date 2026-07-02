import { useState } from 'react'
import type { User } from '../api'

type Props = {
  drivers: User[]
  onConfirm: (driverId: number) => void
  onCancel: () => void
}

export default function ReassignModal({ drivers, onConfirm, onCancel }: Props) {
  const [selected, setSelected] = useState(drivers[0]?.id ?? 0)

  if (drivers.length === 0) {
    return (
      <div className="mt-3 pt-3 border-t text-sm text-gray-500">
        No drivers available.{' '}
        <button onClick={onCancel} className="text-blue-600 hover:underline">Cancel</button>
      </div>
    )
  }

  return (
    <div className="mt-3 pt-3 border-t flex items-center gap-3">
      <select
        value={selected}
        onChange={e => setSelected(Number(e.target.value))}
        className="border rounded px-2 py-1 text-sm"
      >
        {drivers.map(d => (
          <option key={d.id} value={d.id}>{d.name}</option>
        ))}
      </select>
      <button
        onClick={() => onConfirm(selected)}
        className="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
      >
        Confirm
      </button>
      <button
        onClick={onCancel}
        className="text-sm text-gray-500 hover:text-gray-700"
      >
        Cancel
      </button>
    </div>
  )
}
