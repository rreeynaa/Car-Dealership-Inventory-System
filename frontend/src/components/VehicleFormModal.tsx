import { useState } from 'react'
import type { Vehicle, VehicleInput } from '../api/types'
import { validateVehicleForm } from '../lib/validation'
import type { VehicleFormErrors, VehicleFormValues } from '../lib/validation'
import { Alert, Button, Field, Modal } from './ui'

interface Props {
  /** Pass a vehicle to edit it; omit to add a new one. */
  vehicle?: Vehicle
  submitting: boolean
  error: string | null
  onSubmit: (data: VehicleInput) => void
  onClose: () => void
}

export default function VehicleFormModal({ vehicle, submitting, error, onSubmit, onClose }: Props) {
  const [values, setValues] = useState<VehicleFormValues>({
    make: vehicle?.make ?? '',
    model: vehicle?.model ?? '',
    category: vehicle?.category ?? '',
    price: vehicle ? String(vehicle.price) : '',
    quantity: vehicle ? String(vehicle.quantity) : '0',
  })
  const [errors, setErrors] = useState<VehicleFormErrors>({})

  const bind = (key: keyof VehicleFormValues) => ({
    value: values[key],
    error: errors[key],
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => setValues({ ...values, [key]: e.target.value }),
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const found = validateVehicleForm(values)
    setErrors(found)
    if (Object.keys(found).length > 0) return
    onSubmit({
      make: values.make.trim(),
      model: values.model.trim(),
      category: values.category.trim(),
      price: Number(values.price),
      quantity: Number(values.quantity),
    })
  }

  return (
    <Modal title={vehicle ? 'Edit vehicle' : 'Add vehicle'} onClose={onClose}>
      <form onSubmit={handleSubmit} noValidate className="space-y-4">
        {error && <Alert>{error}</Alert>}
        <Field label="Make" {...bind('make')} />
        <Field label="Model" {...bind('model')} />
        <Field label="Category" {...bind('category')} hint="e.g. Sedan, SUV, Truck, Electric" />
        <div className="grid grid-cols-2 gap-3">
          <Field label="Price (USD)" inputMode="decimal" {...bind('price')} />
          <Field label="Quantity" inputMode="numeric" {...bind('quantity')} />
        </div>
        <div className="flex justify-end gap-2 pt-2">
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={submitting}>
            {vehicle ? 'Save changes' : 'Add vehicle'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
