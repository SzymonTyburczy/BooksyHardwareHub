export type HardwareStatus = 'Available' | 'In Use' | 'Repair' | 'Unknown'

export interface Hardware {
  id: number
  name: string
  brand: string
  purchase_date: string | null
  status: HardwareStatus
  notes: string | null
  assigned_to: number | null
  created_at: string
  updated_at: string
}

export interface User {
  id: number
  username: string
  is_admin: boolean
  created_at: string
}

export interface Rental {
  id: number
  hardware_id: number
  user_id: number
  rent_date: string
  return_date: string | null
}

export interface AuthResponse {
  user: User
  token: string
}

export interface CreateHardwarePayload {
  name: string
  brand: string
  purchase_date: string | null
  status: HardwareStatus
  notes?: string
}

export interface CreateUserPayload {
  username: string
  password: string
  is_admin: boolean
}

export interface HardwareFilters {
  search: string
  status: HardwareStatus | ''
  brand: string
}

export interface SortConfig {
  field: keyof Hardware | ''
  direction: 'asc' | 'desc'
}

export interface AiAuditFlag {
  hardware_id: number
  hardware_name: string
  issue: string
  severity: 'low' | 'medium' | 'high'
}

export interface AiAuditResult {
  flags: AiAuditFlag[]
  summary: string
  generated_at: string
}

export interface Toast {
  id: number
  message: string
  type: 'success' | 'error' | 'warning' | 'info'
}
