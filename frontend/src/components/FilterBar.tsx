import type { VehicleFilters } from '../api/types'
import { Button, Field } from './ui'

const KEYS: (keyof VehicleFilters)[] = ['make', 'model', 'category', 'min_price', 'max_price']

export default function FilterBar({
  values,
  onChange,
}: {
  values: VehicleFilters
  onChange: (next: VehicleFilters) => void
}) {
  const set = (key: keyof VehicleFilters) => (e: React.ChangeEvent<HTMLInputElement>) =>
    onChange({ ...values, [key]: e.target.value })
  const hasFilters = KEYS.some((k) => values[k])
  const min = Number(values.min_price)
  const max = Number(values.max_price)
  const rangeError =
    values.min_price && values.max_price && min > max ? 'Min price must not exceed max price' : null

  return (
    <form
      role="search"
      aria-label="Filter vehicles"
      onSubmit={(e) => e.preventDefault()}
      className="rounded-xl bg-white p-4 shadow-xs ring-1 ring-slate-200"
    >
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <Field label="Make" value={values.make ?? ''} onChange={set('make')} placeholder="e.g. Toyota" />
        <Field label="Model" value={values.model ?? ''} onChange={set('model')} placeholder="e.g. Corolla" />
        <Field label="Category" value={values.category ?? ''} onChange={set('category')} placeholder="e.g. SUV" />
        <Field
          label="Min price"
          type="number"
          min={0}
          inputMode="decimal"
          value={values.min_price ?? ''}
          onChange={set('min_price')}
          error={rangeError}
        />
        <Field
          label="Max price"
          type="number"
          min={0}
          inputMode="decimal"
          value={values.max_price ?? ''}
          onChange={set('max_price')}
        />
      </div>
      {hasFilters && (
        <div className="mt-3">
          <Button variant="ghost" size="sm" onClick={() => onChange({})}>
            Clear filters
          </Button>
        </div>
      )}
    </form>
  )
}
