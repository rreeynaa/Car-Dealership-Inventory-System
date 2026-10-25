export type Role = 'user' | 'admin'

export interface User {
  id: number
  email: string
  role: Role
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

export interface Vehicle {
  id: number
  make: string
  model: string
  category: string
  price: number
  quantity: number
  created_at: string
  updated_at: string
}

export interface VehicleList {
  items: Vehicle[]
  total: number
  limit: number
  offset: number
}

export interface VehicleInput {
  make: string
  model: string
  category: string
  price: number
  quantity: number
}

export interface VehicleFilters {
  make?: string
  model?: string
  category?: string
  min_price?: string
  max_price?: string
}
