import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import type { Vehicle, VehicleFilters, VehicleInput } from '../api/types'
import { PAGE_SIZE } from '../api/vehicles'
import { useAuth } from '../auth/AuthContext'
import ConfirmDeleteModal from '../components/ConfirmDeleteModal'
import FilterBar from '../components/FilterBar'
import Pagination from '../components/Pagination'
import RestockModal from '../components/RestockModal'
import VehicleCard from '../components/VehicleCard'
import VehicleFormModal from '../components/VehicleFormModal'
import { useToast } from '../components/toastContext'
import { Alert, Button, Spinner } from '../components/ui'
import { useDebouncedValue } from '../hooks/useDebouncedValue'
import {
  useCreateVehicle,
  useDeleteVehicle,
  usePurchase,
  useRestock,
  useUpdateVehicle,
  useVehicleSearch,
} from '../hooks/useVehicles'

const FILTER_KEYS = ['make', 'model', 'category', 'min_price', 'max_price'] as const

type Dialog =
  | { kind: 'create' }
  | { kind: 'edit'; vehicle: Vehicle }
  | { kind: 'restock'; vehicle: Vehicle }
  | { kind: 'delete'; vehicle: Vehicle }

const messageOf = (err: unknown) => (err instanceof Error ? err.message : 'Something went wrong')

export default function InventoryPage() {
  const { isAdmin } = useAuth()
  const toast = useToast()
  const [params, setParams] = useSearchParams()

  // Filters live in the URL so results can be bookmarked and survive a refresh.
  const urlFilters: VehicleFilters = {}
  for (const key of FILTER_KEYS) {
    const value = params.get(key)
    if (value) urlFilters[key] = value
  }
  const page = Math.max(1, Number(params.get('page')) || 1)

  // Typing updates local state immediately; the request waits for a pause in typing.
  const [draft, setDraft] = useState<VehicleFilters>(urlFilters)
  const debounced = useDebouncedValue(draft, 300)
  const debouncedKey = JSON.stringify(debounced)
  useEffect(() => {
    const next = new URLSearchParams()
    for (const key of FILTER_KEYS) if (debounced[key]) next.set(key, debounced[key])
    // Changing filters resets pagination; skip the write when nothing changed.
    setParams(
      (current) => {
        const same = FILTER_KEYS.every((k) => (current.get(k) ?? '') === (next.get(k) ?? ''))
        return same ? current : next
      },
      { replace: true },
    )
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedKey])

  const min = Number(debounced.min_price)
  const max = Number(debounced.max_price)
  const invalidRange = Boolean(debounced.min_price && debounced.max_price && min > max)
  const activeFilters: VehicleFilters = invalidRange ? {} : urlFilters

  const query = useVehicleSearch(activeFilters, page)

  const purchase = usePurchase()
  const create = useCreateVehicle()
  const update = useUpdateVehicle()
  const remove = useDeleteVehicle()
  const restock = useRestock()

  const [dialog, setDialog] = useState<Dialog | null>(null)
  const [dialogError, setDialogError] = useState<string | null>(null)
  const closeDialog = () => {
    setDialog(null)
    setDialogError(null)
  }

  const setPage = (next: number) => {
    const copy = new URLSearchParams(params)
    if (next <= 1) copy.delete('page')
    else copy.set('page', String(next))
    setParams(copy)
    window.scrollTo({ top: 0 })
  }

  function handlePurchase(vehicle: Vehicle) {
    purchase.mutate(vehicle.id, {
      onSuccess: () => toast.success(`Purchased 1 × ${vehicle.make} ${vehicle.model}`),
      onError: (err) => toast.error(messageOf(err)),
    })
  }

  function run<T>(
    mutate: (vars: T, opts: { onSuccess: () => void; onError: (e: Error) => void }) => void,
    vars: T,
    successMessage: string,
  ) {
    setDialogError(null)
    mutate(vars, {
      onSuccess: () => {
        toast.success(successMessage)
        closeDialog()
      },
      onError: (err) => setDialogError(messageOf(err)),
    })
  }

  const data = query.data
  const purchasingId = purchase.isPending ? purchase.variables : null

  return (
    <div className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Inventory</h1>
          <p className="text-sm text-slate-500">Browse the lot and purchase a vehicle.</p>
        </div>
        {isAdmin && <Button onClick={() => setDialog({ kind: 'create' })}>+ Add vehicle</Button>}
      </div>

      <FilterBar
        values={draft}
        onChange={(next) => {
          setDraft(next)
        }}
      />

      {query.isPending ? (
        <Spinner className="py-20" label="Loading vehicles…" />
      ) : query.isError ? (
        <Alert>
          {messageOf(query.error)}{' '}
          <button type="button" className="font-medium underline" onClick={() => query.refetch()}>
            Try again
          </button>
        </Alert>
      ) : data && data.items.length === 0 ? (
        <div className="rounded-xl bg-white py-16 text-center ring-1 ring-slate-200">
          <p className="font-medium text-slate-900">No vehicles found</p>
          <p className="mt-1 text-sm text-slate-500">Try adjusting or clearing your filters.</p>
        </div>
      ) : (
        data && (
          <>
            <div
              className={`grid gap-4 sm:grid-cols-2 lg:grid-cols-3 ${query.isPlaceholderData ? 'opacity-60' : ''}`}
              aria-busy={query.isFetching}
            >
              {data.items.map((vehicle) => (
                <VehicleCard
                  key={vehicle.id}
                  vehicle={vehicle}
                  isAdmin={isAdmin}
                  purchasing={purchasingId === vehicle.id}
                  onPurchase={handlePurchase}
                  onEdit={(v) => setDialog({ kind: 'edit', vehicle: v })}
                  onRestock={(v) => setDialog({ kind: 'restock', vehicle: v })}
                  onDelete={(v) => setDialog({ kind: 'delete', vehicle: v })}
                />
              ))}
            </div>
            <Pagination page={page} pageSize={PAGE_SIZE} total={data.total} onChange={setPage} />
          </>
        )
      )}

      {dialog?.kind === 'create' && (
        <VehicleFormModal
          submitting={create.isPending}
          error={dialogError}
          onClose={closeDialog}
          onSubmit={(d: VehicleInput) => run(create.mutate, d, 'Vehicle added')}
        />
      )}
      {dialog?.kind === 'edit' && (
        <VehicleFormModal
          vehicle={dialog.vehicle}
          submitting={update.isPending}
          error={dialogError}
          onClose={closeDialog}
          onSubmit={(d: VehicleInput) => run(update.mutate, { id: dialog.vehicle.id, data: d }, 'Vehicle updated')}
        />
      )}
      {dialog?.kind === 'restock' && (
        <RestockModal
          vehicle={dialog.vehicle}
          submitting={restock.isPending}
          error={dialogError}
          onClose={closeDialog}
          onSubmit={(quantity) => run(restock.mutate, { id: dialog.vehicle.id, quantity }, `Added ${quantity} to stock`)}
        />
      )}
      {dialog?.kind === 'delete' && (
        <ConfirmDeleteModal
          vehicle={dialog.vehicle}
          submitting={remove.isPending}
          error={dialogError}
          onClose={closeDialog}
          onConfirm={() => run(remove.mutate, dialog.vehicle.id, 'Vehicle deleted')}
        />
      )}
    </div>
  )
}
