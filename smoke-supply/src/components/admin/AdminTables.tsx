import { useEffect, useState } from 'react';
import { PRODUCTS } from '../../lib/products';
import { loadState, updateState, resetDemoState } from '../../lib/demo-store';
import {
  formatMoney,
  stockStatus,
  statusEmoji,
  statusLabel,
  suggestedReorderQty,
} from '../../lib/inventory-math';
import type { DemoOrder, DemoState, InventoryRecord } from '../../lib/types';

export function AdminOrders() {
  const [orders, setOrders] = useState<DemoOrder[]>([]);
  useEffect(() => {
    const refresh = () => setOrders(loadState().orders);
    refresh();
    window.addEventListener('demo-state-changed', refresh);
    return () => window.removeEventListener('demo-state-changed', refresh);
  }, []);

  function setStatus(id: string, status: DemoOrder['status']) {
    updateState((s) => ({
      ...s,
      orders: s.orders.map((o) => (o.id === id ? { ...o, status } : o)),
    }));
  }

  return (
    <div>
      <p className="notice">Demo orders — including ones placed from the storefront checkout.</p>
      <div className="table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Order</th>
              <th>When</th>
              <th>Customer</th>
              <th>Items</th>
              <th>Total</th>
              <th>Payment</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.id}>
                <td>
                  {o.orderNumber}
                  <div style={{ fontSize: '0.75rem', color: 'var(--muted)' }}>{o.channel}</div>
                </td>
                <td>{new Date(o.createdAt).toLocaleString()}</td>
                <td>
                  {o.customerName}
                  <div style={{ fontSize: '0.75rem' }}>{o.customerPhone}</div>
                </td>
                <td>{o.items.map((i) => `${i.name}×${i.quantity}`).join(', ')}</td>
                <td>{formatMoney(o.total)}</td>
                <td>
                  {o.paymentMethod === 'pay_online' ? 'Online' : 'Pickup'}
                  <div style={{ fontSize: '0.75rem', color: 'var(--muted)' }}>
                    {o.paymentStatus === 'paid_demo' ? 'paid (demo)' : 'unpaid'}
                  </div>
                </td>
                <td>
                  <select
                    aria-label={`Status for ${o.orderNumber}`}
                    value={o.status}
                    onChange={(e) => setStatus(o.id, e.target.value as DemoOrder['status'])}
                  >
                    <option value="pending">pending</option>
                    <option value="preparing">preparing</option>
                    <option value="ready">ready</option>
                    <option value="picked_up">picked_up</option>
                    <option value="cancelled">cancelled</option>
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function AdminProducts() {
  return (
    <div>
      <p className="notice">Static demo catalog ({PRODUCTS.length} fictional SKUs).</p>
      <div className="table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Product</th>
              <th>Brand</th>
              <th>Category</th>
              <th>SKU</th>
              <th>UPC</th>
              <th>Price</th>
            </tr>
          </thead>
          <tbody>
            {PRODUCTS.map((p) => (
              <tr key={p.id}>
                <td>
                  <a href={`/products/${p.slug}/`}>{p.name}</a>
                </td>
                <td>{p.brand}</td>
                <td>{p.category}</td>
                <td>{p.sku}</td>
                <td>{p.upc}</td>
                <td>{formatMoney(p.price)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function AdminInventory() {
  const [rows, setRows] = useState<InventoryRecord[]>([]);
  useEffect(() => {
    const refresh = () => setRows(loadState().inventory);
    refresh();
    window.addEventListener('demo-state-changed', refresh);
    return () => window.removeEventListener('demo-state-changed', refresh);
  }, []);

  return (
    <div>
      <p className="notice">POS-side inventory (simulated). Website stock updates after sync.</p>
      <div className="table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Product</th>
              <th>SKU</th>
              <th>Qty</th>
              <th>Min</th>
              <th>Daily velocity</th>
              <th>Status</th>
              <th>Suggested reorder</th>
              <th>Supplier</th>
              <th>Last updated</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => {
              const product = PRODUCTS.find((p) => p.id === r.productId);
              const status = stockStatus(r);
              return (
                <tr key={r.sku}>
                  <td>{product?.name ?? r.productId}</td>
                  <td>{r.sku}</td>
                  <td>{r.quantity}</td>
                  <td>{r.minimum}</td>
                  <td>{r.dailyVelocity}</td>
                  <td>
                    {statusEmoji(status)} {statusLabel(status)}
                  </td>
                  <td>{suggestedReorderQty(r)}</td>
                  <td>{r.supplier}</td>
                  <td>{new Date(r.lastUpdated).toLocaleString()}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function AdminCustomers() {
  const [state, setState] = useState<DemoState | null>(null);
  useEffect(() => setState(loadState()), []);
  if (!state) return null;
  return (
    <div>
      <p className="notice">Demo customers only — no real personal data.</p>
      <div className="table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Name</th>
              <th>Phone</th>
              <th>Email</th>
              <th>Orders</th>
            </tr>
          </thead>
          <tbody>
            {state.customers.map((c) => (
              <tr key={c.id}>
                <td>{c.name}</td>
                <td>{c.phone}</td>
                <td>{c.email}</td>
                <td>{c.orderCount}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function AdminSettings() {
  return (
    <div className="card">
      <h2>Demo settings</h2>
      <p>Connection: Demo Connection — Simulated</p>
      <p>Payment processor: Demo simulation (pay online or pay at pickup). Production would use the store’s real processor.</p>
      <p>Age verification: Notice only — not legal verification</p>
      <button
        type="button"
        className="btn btn-demo"
        style={{ marginTop: '1rem' }}
        onClick={() => {
          resetDemoState();
          window.location.reload();
        }}
      >
        Reset all demo data
      </button>
      <p style={{ marginTop: '0.75rem', fontSize: '0.9rem', color: 'var(--muted)' }}>
        Clears localStorage cart and simulated POS state back to seed data.
      </p>
    </div>
  );
}
