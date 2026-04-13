import type { Hardware, HardwareStatus, User } from '@/types'

export const MOCK_HARDWARE: Hardware[] = [
  {
    id: 1,
    name: 'Apple iPhone 13 Pro Max',
    brand: 'Apple',
    purchase_date: '2021-11-23',
    status: 'Available',
    notes: null,
    assigned_to: null,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    name: 'Apple MacBook Pro 13',
    brand: 'Apple',
    purchase_date: '2021-12-20',
    status: 'In Use',
    notes: null,
    assigned_to: 2,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 3,
    name: 'Razer Basilisk V2',
    brand: 'Razer',
    purchase_date: '2021-06-05',
    status: 'Repair',
    notes: null,
    assigned_to: null,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 4,
    name: 'SAMSUNG Galaxy S21',
    brand: 'Samsung',
    purchase_date: '2021-11-23',
    status: 'Available',
    notes: null,
    assigned_to: null,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 5,
    name: 'Dell XPS 15 9510',
    brand: 'Dell',
    purchase_date: '2022-03-15',
    status: 'Available',
    notes: '⚠️ Battery swelling, do not issue without service.',
    assigned_to: null,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 6,
    name: 'Logitech MX Master 3',
    brand: 'Logitech',
    purchase_date: '2027-10-10',
    status: 'Available',
    notes: null,
    assigned_to: null,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 7,
    name: 'Sony WH-1000XM4',
    brand: 'Sony',
    purchase_date: '2022-01-12',
    status: 'In Use',
    notes: null,
    assigned_to: 2,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 8,
    name: 'Duplicate ID Test Laptop',
    brand: 'Lenovo',
    purchase_date: '2023-01-01',
    status: 'Repair',
    notes: null,
    assigned_to: null,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 9,
    name: 'iPad Pro 12.9',
    brand: 'Apple',
    purchase_date: '2023-05-22',
    status: 'Available',
    notes: null,
    assigned_to: null,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 10,
    name: 'Unknown Device',
    brand: 'Unknown',
    purchase_date: null,
    status: 'Unknown',
    notes: null,
    assigned_to: null,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 11,
    name: 'MacBook Air M2',
    brand: 'Apple',
    purchase_date: '2023-08-01',
    status: 'Available',
    notes: '⚠️ Returned with liquid damage. Keyboard sticky.',
    assigned_to: null,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
]

export const MOCK_USERS: User[] = [
  {
    id: 1,
    username: 'admin',
    is_admin: true,
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    username: 'j.doe',
    is_admin: false,
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 3,
    username: 'a.smith',
    is_admin: false,
    created_at: '2024-02-15T00:00:00Z',
  },
]

// Mock audit flags generated from data analysis
export const MOCK_AUDIT_FLAGS = [
  {
    hardware_id: 6,
    hardware_name: 'Logitech MX Master 3',
    issue: 'Purchase date is in the future (2027-10-10). This may be a data entry error.',
    severity: 'high' as const,
  },
  {
    hardware_id: 5,
    hardware_name: 'Dell XPS 15 9510',
    issue: 'Notes indicate battery swelling — a safety hazard. Device is marked Available but should be in Repair.',
    severity: 'high' as const,
  },
  {
    hardware_id: 11,
    hardware_name: 'MacBook Air M2',
    issue: 'Notes indicate liquid damage and sticky keyboard. Device is Available but may need servicing.',
    severity: 'medium' as const,
  },
  {
    hardware_id: 10,
    hardware_name: 'Unknown Device',
    issue: 'Status is "Unknown" — device has no brand or purchase date. Needs identification.',
    severity: 'medium' as const,
  },
  {
    hardware_id: 3,
    hardware_name: 'Razer Basilisk V2',
    issue: 'Device has been in Repair status since 2021. Consider escalating or writing off.',
    severity: 'low' as const,
  },
]

export const MOCK_AUDIT_SUMMARY =
  'Inventory audit complete. Found 5 issues: 2 high-severity (safety risk + data anomaly), 2 medium-severity, 1 low-severity. Immediate action recommended for Dell XPS 15 9510 (battery swelling) and Logitech MX Master 3 (invalid purchase date).'

// Simple keyword-based mock semantic search
export function mockSemanticSearch(query: string, hardware: Hardware[]): Hardware[] {
  const q = query.toLowerCase()

  // Keyword maps for natural language → device types
  const keywordMap: Record<string, string[]> = {
    'mobile': ['iphone', 'galaxy', 'ipad', 'samsung', 'apple'],
    'phone': ['iphone', 'galaxy', 'samsung', 'sony'],
    'laptop': ['macbook', 'xps', 'dell', 'lenovo'],
    'mouse': ['basilisk', 'mx master', 'logitech', 'razer'],
    'headphone': ['sony', 'wh-1000', 'headphones'],
    'audio': ['sony', 'wh-1000'],
    'test': ['iphone', 'galaxy', 'ipad', 'samsung'],
    'develop': ['macbook', 'xps', 'laptop'],
    'meeting': ['headphone', 'sony'],
    'portable': ['iphone', 'galaxy', 'ipad', 'macbook air'],
    'apple': ['apple', 'iphone', 'ipad', 'macbook'],
    'keyboard': ['razer', 'logitech'],
    'wireless': ['logitech', 'sony', 'apple'],
  }

  const matchedKeywords = Object.entries(keywordMap)
    .filter(([keyword]) => q.includes(keyword))
    .flatMap(([, terms]) => terms)

  if (matchedKeywords.length === 0) {
    // Fallback to name/brand text search
    return hardware.filter(
      (h) =>
        h.name.toLowerCase().includes(q) ||
        h.brand.toLowerCase().includes(q),
    )
  }

  return hardware.filter((h) => {
    const combined = `${h.name} ${h.brand}`.toLowerCase()
    return matchedKeywords.some((term) => combined.includes(term))
  })
}

export function getStatusCounts(hardware: Hardware[]): Record<HardwareStatus, number> {
  return {
    Available: hardware.filter((h) => h.status === 'Available').length,
    'In Use': hardware.filter((h) => h.status === 'In Use').length,
    Repair: hardware.filter((h) => h.status === 'Repair').length,
    Unknown: hardware.filter((h) => h.status === 'Unknown').length,
  }
}
