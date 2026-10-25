import { useState } from 'react'
import type { Vehicle } from '../api/types'
import { Alert, Button, Field, Modal } from './ui'

interface Props {
  vehicle: Vehicle
  submitting: boolean
  error: string | null
  onSubmit: (quantity: number) => void
  onClose: () => void
}

export default function RestockModal({ vehicle, submitting, error, onSubmit, onClose }: Props) {
  const [value, setValue] = useState('1')
  const [fieldError, setFieldError] = useState<string | null>(null)

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const quantity = Number(value)
    if (!Number.isInteger(quantity) || quantity < 1 || quantity > 1_000_000) {
      setFieldError('Enter a whole number between 1 and 1,000,000')
      return
    }
    setFieldError(null)
    onSubmit(quantity)
  }

  return (
    <Modal title={`Restock ${vehicle.make} ${vehicle.model}`} onClose={onClose}>
      <form onSubmit={handleSubmit} noValidate className="space-y-4">
        <p className="text-sm text-slate-600">Currently {vehicle.quantity} in stock.</p>
        {error && <Alert>{error}</Alert>}
        <Field
          label="Units to add"
          type="number"
          min={1}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          error={fieldError}
        />
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={submitting}>
            Add stock
          </Button>
        </div>
      </form>
    </Modal>
  )
}
