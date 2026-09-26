export type CategoryId =
  | 'cigarettes'
  | 'cigars'
  | 'tobacco'
  | 'nicotine-pouches'
  | 'vapes'
  | 'accessories'
  | 'lighters';

export type StockStatus = 'healthy' | 'low' | 'reorder' | 'out';

export interface Product {
  id: string;
  slug: string;
  name: string;
  brand: string;
  category: CategoryId;
  sku: string;
  upc: string;
  price: number;
  description: string;
  attributes: Record<string, string>;
  imageHue: number;
  featured?: boolean;
  complianceNote?: string;
}

export interface InventoryRecord {
  productId: string;
  sku: string;
  quantity: number;
  minimum: number;
  dailyVelocity: number;
  leadTimeDays: number;
  supplier: string;
  lastUpdated: string;
}

export interface CartItem {
  productId: string;
  quantity: number;
}

export interface DemoCustomer {
  id: string;
  name: string;
  phone: string;
  email: string;
  orderCount: number;
}

export interface OrderLine {
  productId: string;
  name: string;
  sku: string;
  quantity: number;
  unitPrice: number;
}

export type OrderStatus = 'pending' | 'preparing' | 'ready' | 'picked_up' | 'cancelled';

export type PaymentMethod = 'pay_at_pickup' | 'pay_online';

export type PaymentStatus = 'unpaid' | 'paid_demo';

export interface DemoOrder {
  id: string;
  orderNumber: string;
  createdAt: string;
  status: OrderStatus;
  channel: 'online' | 'in_store';
  customerName: string;
  customerPhone: string;
  customerEmail: string;
  items: OrderLine[];
  subtotal: number;
  tax: number;
  total: number;
  pickupNotes?: string;
  estimatedReadyMinutes: number;
  paymentMethod: PaymentMethod;
  paymentStatus: PaymentStatus;
}

export interface SaleEvent {
  id: string;
  date: string;
  productId: string;
  quantity: number;
  revenue: number;
  channel: 'online' | 'in_store';
}

export interface SyncResult {
  syncedAt: string;
  productsSynced: number;
  inventoryRecords: number;
  ordersSynced: number;
  message: string;
}

export interface DemoState {
  version: number;
  inventory: InventoryRecord[];
  websiteInventory: InventoryRecord[];
  orders: DemoOrder[];
  customers: DemoCustomer[];
  sales: SaleEvent[];
  lastSyncAt: string | null;
  syncLog: string[];
}
