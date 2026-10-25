import type { Vehicle } from '../api/types'
import { Alert, Button, Modal } from './ui'

export default function ConfirmDeleteModal({
  vehicle,
  submitting,
  error,
  onConfirm,
  onClose,
}: {
  vehicle: Vehicle
  submitting: boolean
  error: string | null
  onConfirm: () => void
  onClose: () => void
}) {
  return (
    <Modal title="Delete vehicle?" onClose={onClose}>
      <div className="space-y-4">
        <p className="text-sm text-slate-600">
          <strong>
            {vehicle.make} {vehicle.model}
          </strong>{' '}
          will be permanently removed from the inventory. This cannot be undone.
        </p>
        {error && <Alert>{error}</Alert>}
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="danger" onClick={onConfirm} loading={submitting}>
            Delete
          </Button>
        </div>
      </div>
    </Modal>
  )
}
