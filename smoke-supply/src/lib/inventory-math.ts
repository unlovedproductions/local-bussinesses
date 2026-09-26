import type { InventoryRecord, StockStatus } from './types';

export function stockStatus(record: InventoryRecord): StockStatus {
  if (record.quantity <= 0) return 'out';
  if (record.quantity < record.minimum) return 'reorder';
  if (record.quantity < record.minimum * 1.5) return 'low';
  return 'healthy';
}

export function statusLabel(status: StockStatus): string {
  switch (status) {
    case 'healthy':
      return 'Healthy stock';
    case 'low':
      return 'Low stock';
    case 'reorder':
      return 'Reorder recommended';
    case 'out':
      return 'Out of stock';
    default: {
      const _exhaustive: never = status;
      return _exhaustive;
    }
  }
}

export function statusEmoji(status: StockStatus): string {
  switch (status) {
    case 'healthy':
      return '🟢';
    case 'low':
      return '🟡';
    case 'reorder':
    case 'out':
      return '🔴';
    default: {
      const _exhaustive: never = status;
      return _exhaustive;
    }
  }
}

/**
 * Demo reorder suggestion — NOT a universal inventory formula.
 * Visible assumptions: cover lead time + buffer to restore minimum.
 */
export function suggestedReorderQty(record: InventoryRecord): number {
  const cover = Math.ceil(record.dailyVelocity * record.leadTimeDays);
  const gap = Math.max(0, record.minimum - record.quantity);
  const buffer = Math.ceil(record.dailyVelocity * 3);
  return Math.max(cover + gap + buffer, record.minimum);
}

export function inventoryValue(records: InventoryRecord[], priceBySku: Map<string, number>): number {
  return records.reduce((sum, r) => sum + r.quantity * (priceBySku.get(r.sku) ?? 0), 0);
}

export function formatMoney(n: number): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n);
}
