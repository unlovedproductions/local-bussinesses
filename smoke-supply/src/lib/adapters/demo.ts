import type { DemoOrder, DemoState, InventoryRecord, SyncResult } from '../types';
import type { InventoryAdapter, PosAdapter } from './types';

export class DemoPosAdapter implements PosAdapter {
  constructor(
    private getState: () => DemoState,
    private setState: (updater: (s: DemoState) => DemoState) => void,
  ) {}

  listInventory(): InventoryRecord[] {
    return this.getState().inventory.map((r) => ({ ...r }));
  }

  recordSale(sku: string, qty: number, channel: 'in_store' | 'online'): void {
    this.setState((s) => {
      const inventory = s.inventory.map((r) =>
        r.sku === sku
          ? {
              ...r,
              quantity: Math.max(0, r.quantity - qty),
              lastUpdated: new Date().toISOString(),
            }
          : r,
      );
      const product = inventory.find((r) => r.sku === sku);
      const sales = [
        {
          id: `sale-${Date.now()}`,
          date: new Date().toISOString(),
          productId: product?.productId ?? sku,
          quantity: qty,
          revenue: 0,
          channel,
        },
        ...s.sales,
      ];
      return {
        ...s,
        inventory,
        sales,
        syncLog: [
          `[POS] Recorded ${channel} sale: ${sku} × ${qty}`,
          ...s.syncLog,
        ].slice(0, 40),
      };
    });
  }

  pushOrder(order: DemoOrder): void {
    this.setState((s) => {
      const inventory = s.inventory.map((r) => {
        const line = order.items.find((i) => i.sku === r.sku);
        if (!line) return r;
        return {
          ...r,
          quantity: Math.max(0, r.quantity - line.quantity),
          lastUpdated: new Date().toISOString(),
        };
      });
      return {
        ...s,
        inventory,
        orders: [order, ...s.orders],
        syncLog: [
          `[POS] Received online order ${order.orderNumber}`,
          ...s.syncLog,
        ].slice(0, 40),
      };
    });
  }

  sync(): SyncResult {
    const now = new Date().toISOString();
    let result: SyncResult = {
      syncedAt: now,
      productsSynced: 0,
      inventoryRecords: 0,
      ordersSynced: 0,
      message: 'Sync failed',
    };

    this.setState((s) => {
      const websiteInventory = s.inventory.map((r) => ({ ...r }));
      result = {
        syncedAt: now,
        productsSynced: websiteInventory.length,
        inventoryRecords: websiteInventory.length,
        ordersSynced: s.orders.length,
        message: 'Simulated sync: POS inventory copied to website catalog.',
      };
      return {
        ...s,
        websiteInventory,
        lastSyncAt: now,
        syncLog: [`[Sync] ${result.message}`, ...s.syncLog].slice(0, 40),
      };
    });

    return result;
  }

  getConnectionStatus() {
    const s = this.getState();
    return {
      label: 'Demo Connection — Simulated',
      productsSynced: s.websiteInventory.length,
      inventoryRecords: s.inventory.length,
      ordersSynced: s.orders.length,
      apiStatus: 'Simulation Active',
      lastSync: s.lastSyncAt,
    };
  }
}

export class DemoInventoryAdapter implements InventoryAdapter {
  constructor(
    private getState: () => DemoState,
    private setState: (updater: (s: DemoState) => DemoState) => void,
  ) {}

  listWebsiteInventory(): InventoryRecord[] {
    return this.getState().websiteInventory.map((r) => ({ ...r }));
  }

  applyFromPos(posRecords: InventoryRecord[]): void {
    this.setState((s) => ({
      ...s,
      websiteInventory: posRecords.map((r) => ({ ...r })),
    }));
  }

  decrementForOrder(sku: string, qty: number): void {
    this.setState((s) => ({
      ...s,
      websiteInventory: s.websiteInventory.map((r) =>
        r.sku === sku
          ? {
              ...r,
              quantity: Math.max(0, r.quantity - qty),
              lastUpdated: new Date().toISOString(),
            }
          : r,
      ),
    }));
  }
}

/** Integration layer — website talks here, not directly to a vendor API. */
export class IntegrationService {
  constructor(
    public pos: PosAdapter,
    public inventory: InventoryAdapter,
  ) {}

  syncPosToWebsite(): SyncResult {
    return this.pos.sync();
  }

  placeOnlineOrder(order: DemoOrder): void {
    for (const line of order.items) {
      this.inventory.decrementForOrder(line.sku, line.quantity);
    }
    this.pos.pushOrder(order);
  }
}
