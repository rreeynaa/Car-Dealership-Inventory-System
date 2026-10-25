import type { Vehicle } from '../api/types'
import { formatPrice, stockStatus } from '../lib/format'
import { Badge, Button } from './ui'

interface Props {
  vehicle: Vehicle
  isAdmin: boolean
  purchasing: boolean
  onPurchase: (v: Vehicle) => void
  onEdit: (v: Vehicle) => void
  onRestock: (v: Vehicle) => void
  onDelete: (v: Vehicle) => void
}

export default function VehicleCard({ vehicle, isAdmin, purchasing, onPurchase, onEdit, onRestock, onDelete }: Props) {
  const status = stockStatus(vehicle.quantity)
  const soldOut = vehicle.quantity === 0
  const name = `${vehicle.make} ${vehicle.model}`

  return (
    <article
      aria-label={name}
      className="flex flex-col rounded-xl bg-white p-5 shadow-xs ring-1 ring-slate-200 transition hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className="text-base font-semibold text-slate-900">{name}</h3>
          <p className="text-sm text-slate-500">{vehicle.category}</p>
        </div>
        <Badge tone={status.tone}>{status.label}</Badge>
      </div>

      <p className="mt-4 text-2xl font-bold text-slate-900">{formatPrice(vehicle.price)}</p>

      <div className="mt-5 flex-1" />
      <Button
        onClick={() => onPurchase(vehicle)}
        disabled={soldOut}
        loading={purchasing}
        aria-label={soldOut ? `${name} is sold out` : `Purchase ${name}`}
        className="w-full"
      >
        {soldOut ? 'Sold out' : 'Purchase'}
      </Button>

      {isAdmin && (
        <div className="mt-3 flex gap-2 border-t border-slate-100 pt-3">
          <Button variant="secondary" size="sm" onClick={() => onEdit(vehicle)} aria-label={`Edit ${name}`}>
            Edit
          </Button>
          <Button variant="secondary" size="sm" onClick={() => onRestock(vehicle)} aria-label={`Restock ${name}`}>
            Restock
          </Button>
          <Button variant="ghost" size="sm" className="ml-auto text-red-600" onClick={() => onDelete(vehicle)} aria-label={`Delete ${name}`}>
            Delete
          </Button>
        </div>
      )}
    </article>
  )
}
