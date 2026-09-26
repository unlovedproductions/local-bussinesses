import { PRODUCTS } from './products';
import type {
  DemoCustomer,
  DemoOrder,
  DemoState,
  InventoryRecord,
  SaleEvent,
} from './types';

const SUPPLIERS = [
  'Cascade Wholesale Demo',
  'Pacific Supply Co. (Demo)',
  'Ridge Distributors Demo',
  'Harbor Import Demo',
];

function hash(str: string): number {
  let h = 0;
  for (let i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) >>> 0;
  return h;
}

function inventoryForProduct(productId: string, sku: string, i: number): InventoryRecord {
  const h = hash(sku);
  const quantity = 8 + (h % 90);
  const minimum = 10 + (h % 15);
  const dailyVelocity = Number((0.5 + (h % 50) / 10).toFixed(1));
  const leadTimeDays = 3 + (h % 5);
  const supplier = SUPPLIERS[i % SUPPLIERS.length];
  return {
    productId,
    sku,
    quantity,
    minimum,
    dailyVelocity,
    leadTimeDays,
    supplier,
    lastUpdated: new Date().toISOString(),
  };
}

export function buildSeedInventory(): InventoryRecord[] {
  return PRODUCTS.map((p, i) => inventoryForProduct(p.id, p.sku, i));
}

/** Force a few low-stock SKUs so the demo always shows alerts. */
export function applyDemoLowStock(records: InventoryRecord[]): InventoryRecord[] {
  const targets = [
    { sku: 'CIG-RDG-RED-20', quantity: 8, minimum: 12 },
    { sku: 'PCH-FRS-MNT-6', quantity: 5, minimum: 10 },
    { sku: 'VAP-VTR-BLU-D', quantity: 4, minimum: 8 },
    { sku: 'LGT-SPK-DSP-1', quantity: 9, minimum: 20 },
    { sku: 'TOB-BRK-VIR-50', quantity: 6, minimum: 10 },
  ];
  return records.map((r) => {
    const t = targets.find((x) => x.sku === r.sku);
    return t ? { ...r, quantity: t.quantity, minimum: t.minimum } : r;
  });
}

export const SEED_CUSTOMERS: DemoCustomer[] = [
  { id: 'cust-1', name: 'Alex Rivera', phone: '(555) 010-1001', email: 'alex.demo@example.com', orderCount: 4 },
  { id: 'cust-2', name: 'Jordan Lee', phone: '(555) 010-1002', email: 'jordan.demo@example.com', orderCount: 2 },
  { id: 'cust-3', name: 'Sam Patel', phone: '(555) 010-1003', email: 'sam.demo@example.com', orderCount: 7 },
  { id: 'cust-4', name: 'Casey Morgan', phone: '(555) 010-1004', email: 'casey.demo@example.com', orderCount: 1 },
  { id: 'cust-5', name: 'Riley Chen', phone: '(555) 010-1005', email: 'riley.demo@example.com', orderCount: 3 },
];

function daysAgo(n: number): string {
  const d = new Date();
  d.setDate(d.getDate() - n);
  d.setHours(10 + (n % 8), (n * 7) % 60, 0, 0);
  return d.toISOString();
}

export function buildSeedOrders(): DemoOrder[] {
  const lines = (sku: string, name: string, productId: string, qty: number, price: number) => [
    { productId, name, sku, quantity: qty, unitPrice: price },
  ];

  return [
    {
      id: 'ord-seed-1',
      orderNumber: 'SS-10041',
      createdAt: daysAgo(0),
      status: 'preparing',
      channel: 'online',
      customerName: 'Alex Rivera',
      customerPhone: '(555) 010-1001',
      customerEmail: 'alex.demo@example.com',
      items: lines('CIG-RDG-RED-20', 'Ridge Red Soft Pack', 'ridge-red-pack', 2, 9.49),
      subtotal: 18.98,
      tax: 0,
      total: 18.98,
      estimatedReadyMinutes: 25,
      paymentMethod: 'pay_online',
      paymentStatus: 'paid_demo',
    },
    {
      id: 'ord-seed-2',
      orderNumber: 'SS-10040',
      createdAt: daysAgo(0),
      status: 'ready',
      channel: 'online',
      customerName: 'Jordan Lee',
      customerPhone: '(555) 010-1002',
      customerEmail: 'jordan.demo@example.com',
      items: [
        ...lines('PCH-FRS-MNT-6', 'Frostline Mint 6mg', 'frostline-mint-6', 1, 5.99),
        ...lines('LGT-SPK-DSP-1', 'Sparkline Disposable Lighter', 'sparkline-disposable', 1, 1.49),
      ],
      subtotal: 7.48,
      tax: 0,
      total: 7.48,
      estimatedReadyMinutes: 20,
      paymentMethod: 'pay_at_pickup',
      paymentStatus: 'unpaid',
    },
    {
      id: 'ord-seed-3',
      orderNumber: 'SS-10039',
      createdAt: daysAgo(1),
      status: 'picked_up',
      channel: 'online',
      customerName: 'Sam Patel',
      customerPhone: '(555) 010-1003',
      customerEmail: 'sam.demo@example.com',
      items: lines('CGR-PLZ-MM-5', 'Plaza Machine-Made 5-Pack', 'plaza-machine-5pk', 1, 12.99),
      subtotal: 12.99,
      tax: 0,
      total: 12.99,
      estimatedReadyMinutes: 30,
      paymentMethod: 'pay_online',
      paymentStatus: 'paid_demo',
    },
    {
      id: 'ord-seed-4',
      orderNumber: 'SS-10038',
      createdAt: daysAgo(1),
      status: 'picked_up',
      channel: 'in_store',
      customerName: 'Walk-in Customer',
      customerPhone: '—',
      customerEmail: '—',
      items: lines('VAP-VTR-BLU-D', 'Vaportrail Blue Disposable', 'vaportrail-blue-disposable', 1, 18.99),
      subtotal: 18.99,
      tax: 0,
      total: 18.99,
      estimatedReadyMinutes: 0,
      paymentMethod: 'pay_at_pickup',
      paymentStatus: 'paid_demo',
    },
    {
      id: 'ord-seed-5',
      orderNumber: 'SS-10037',
      createdAt: daysAgo(2),
      status: 'picked_up',
      channel: 'online',
      customerName: 'Casey Morgan',
      customerPhone: '(555) 010-1004',
      customerEmail: 'casey.demo@example.com',
      items: lines('TOB-BRK-VIR-50', 'Brookside Virginia Pipe Blend', 'brookside-virginia', 1, 14.99),
      subtotal: 14.99,
      tax: 0,
      total: 14.99,
      estimatedReadyMinutes: 25,
      paymentMethod: 'pay_at_pickup',
      paymentStatus: 'unpaid',
    },
  ];
}

export function buildSeedSales(): SaleEvent[] {
  const events: SaleEvent[] = [];
  const sample = PRODUCTS.slice(0, 20);
  for (let day = 0; day < 14; day++) {
    for (let i = 0; i < 6; i++) {
      const product = sample[(day * 3 + i) % sample.length];
      const qty = 1 + ((day + i) % 3);
      events.push({
        id: `sale-${day}-${i}`,
        date: daysAgo(day),
        productId: product.id,
        quantity: qty,
        revenue: Number((product.price * qty).toFixed(2)),
        channel: i % 3 === 0 ? 'online' : 'in_store',
      });
    }
  }
  return events;
}

export const DEMO_STATE_VERSION = 2;
export const STORAGE_KEY = 'smoke-supply-demo-v1';
export const CART_KEY = 'smoke-supply-cart-v1';

export function createInitialState(): DemoState {
  const inventory = applyDemoLowStock(buildSeedInventory());
  return {
    version: DEMO_STATE_VERSION,
    inventory: inventory.map((r) => ({ ...r })),
    websiteInventory: inventory.map((r) => ({ ...r })),
    orders: buildSeedOrders(),
    customers: SEED_CUSTOMERS,
    sales: buildSeedSales(),
    lastSyncAt: new Date().toISOString(),
    syncLog: ['Demo environment initialized with simulated POS inventory.'],
  };
}
