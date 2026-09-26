import type { DemoOrder, InventoryRecord, SyncResult } from './types';

/**
 * Replaceable POS adapter interface.
 * Phase 2: swap DemoPosAdapter for an ActualPosAdapter once the store's POS is known.
 * Do not invent a vendor API here.
 */
export interface PosAdapter {
  listInventory(): InventoryRecord[];
  recordSale(sku: string, qty: number, channel: 'in_store' | 'online'): void;
  pushOrder(order: DemoOrder): void;
  sync(): SyncResult;
  getConnectionStatus(): {
    label: string;
    productsSynced: number;
    inventoryRecords: number;
    ordersSynced: number;
    apiStatus: string;
    lastSync: string | null;
  };
}

export interface InventoryAdapter {
  listWebsiteInventory(): InventoryRecord[];
  applyFromPos(posRecords: InventoryRecord[]): void;
  decrementForOrder(sku: string, qty: number): void;
}
