import { apiRequest } from './client'
import type { Vehicle, VehicleFilters, VehicleInput, VehicleList } from './types'

export const PAGE_SIZE = 12

export const vehiclesApi = {
  search: (filters: VehicleFilters, page: number) =>
    apiRequest<VehicleList>('/api/vehicles/search', {
      params: { ...filters, limit: PAGE_SIZE, offset: (page - 1) * PAGE_SIZE },
    }),
  create: (data: VehicleInput) =>
    apiRequest<Vehicle>('/api/vehicles', { method: 'POST', body: data }),
  update: (id: number, data: Partial<VehicleInput>) =>
    apiRequest<Vehicle>(`/api/vehicles/${id}`, { method: 'PUT', body: data }),
  remove: (id: number) => apiRequest<void>(`/api/vehicles/${id}`, { method: 'DELETE' }),
  purchase: (id: number) =>
    apiRequest<Vehicle>(`/api/vehicles/${id}/purchase`, { method: 'POST' }),
  restock: (id: number, quantity: number) =>
    apiRequest<Vehicle>(`/api/vehicles/${id}/restock`, { method: 'POST', body: { quantity } }),
}
