import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { vehiclesApi } from '../api/vehicles'
import type { VehicleFilters, VehicleInput } from '../api/types'

const KEY = 'vehicles'

export function useVehicleSearch(filters: VehicleFilters, page: number) {
  return useQuery({
    queryKey: [KEY, filters, page],
    queryFn: () => vehiclesApi.search(filters, page),
    placeholderData: keepPreviousData,
  })
}

/** All inventory mutations refresh the list on success. */
function useInventoryMutation<TVars>(fn: (vars: TVars) => Promise<unknown>) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: fn,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: [KEY] }),
    // A failed purchase (e.g. someone else bought the last unit) means our list is stale.
    onError: () => queryClient.invalidateQueries({ queryKey: [KEY] }),
  })
}

export const usePurchase = () => useInventoryMutation((id: number) => vehiclesApi.purchase(id))
export const useCreateVehicle = () => useInventoryMutation((data: VehicleInput) => vehiclesApi.create(data))
export const useUpdateVehicle = () =>
  useInventoryMutation(({ id, data }: { id: number; data: Partial<VehicleInput> }) => vehiclesApi.update(id, data))
export const useDeleteVehicle = () => useInventoryMutation((id: number) => vehiclesApi.remove(id))
export const useRestock = () =>
  useInventoryMutation(({ id, quantity }: { id: number; quantity: number }) => vehiclesApi.restock(id, quantity))
