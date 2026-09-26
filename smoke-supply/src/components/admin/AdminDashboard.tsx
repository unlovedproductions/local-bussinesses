import { useEffect, useMemo, useState } from 'react';
import { PRODUCTS } from '../../lib/products';
import { loadState } from '../../lib/demo-store';
import { formatMoney, stockStatus, suggestedReorderQty } from '../../lib/inventory-math';
import type { DemoState } from '../../lib/types';

function todayPrefix() {
  return new Date().toISOString().slice(0, 10);
}

export default function AdminDashboard() {
  const [state, setState] = useState<DemoState | null>(null);

  useEffect(() => {
    const refresh = () => setState(loadState());
    refresh();
    window.addEventListener('demo-state-changed', refresh);
    return () => window.removeEventListener('demo-state-changed', refresh);
  }, []);

  const metrics = useMemo(() => {
    if (!state) return null;
    const day = todayPrefix();
    const onlineToday = state.orders.filter((o) => o.channel === 'online' && o.createdAt.startsWith(day));
    const storeSalesToday = state.sales
      .filter((s) => s.channel === 'in_store' && s.date.startsWith(day))
      .reduce((n, s) => n + s.revenue, 0);
    const low = state.inventory.filter((r) => {
      const s = stockStatus(r);
      return s === 'low' || s === 'reorder' || s === 'out';
    });
    const reorder = state.inventory.filter((r) => stockStatus(r) === 'reorder' || stockStatus(r) === 'out');
    const priceBySku = new Map(PRODUCTS.map((p) => [p.sku, p.price]));
    const value = state.inventory.reduce((n, r) => n + r.quantity * (priceBySku.get(r.sku) ?? 0), 0);
    const sold = new Map<string, number>();
    for (const s of state.sales) sold.set(s.productId, (sold.get(s.productId) ?? 0) + s.quantity);
    const top = [...sold.entries()]
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([id, qty]) => ({ product: PRODUCTS.find((p) => p.id === id), qty }));
    return {
      onlineCount: onlineToday.length,
      storeSalesToday,
      lowCount: low.length,
      reorderCount: reorder.length,
      value,
      top,
      recent: state.orders.slice(0, 5),
      needsReorder: reorder.slice(0, 5).map((r) => ({
        ...r,
        suggested: suggestedReorderQty(r),
        name: PRODUCTS.find((p) => p.id === r.productId)?.name ?? r.sku,
      })),
    };
  }, [state]);

  if (!metrics) return <p>Loading demo metrics…</p>;

  return (
    <div>
      <p className="notice">All numbers below are demo data stored in this browser.</p>
      <div className="metric-grid">
        <div className="metric">
          <div className="label">Today’s online orders</div>
          <div className="value">{metrics.onlineCount}</div>
        </div>
        <div className="metric">
          <div className="label">Today’s store sales</div>
          <div className="value">{formatMoney(metrics.storeSalesToday)}</div>
        </div>
        <div className="metric">
          <div className="label">Low-stock products</div>
          <div className="value">{metrics.lowCount}</div>
        </div>
        <div className="metric">
          <div className="label">Need reorder</div>
          <div className="value">{metrics.reorderCount}</div>
        </div>
        <div className="metric">
          <div className="label">Inventory value</div>
          <div className="value">{formatMoney(metrics.value)}</div>
        </div>
      </div>

      <div className="grid-2" style={{ marginTop: '1.25rem' }}>
        <div className="card">
          <h2>Top-selling products (demo)</h2>
          <ul>
            {metrics.top.map((t) => (
              <li key={t.product?.id ?? Math.random()}>
                {t.product?.name ?? 'Unknown'} — {t.qty} units
              </li>
            ))}
          </ul>
        </div>
        <div className="card">
          <h2>Products needing reorder</h2>
          <ul>
            {metrics.needsReorder.map((r) => (
              <li key={r.sku}>
                {r.name}: {r.quantity} on hand · suggest {r.suggested}
              </li>
            ))}
          </ul>
          <a href="/admin/reorder/">View reorder engine</a>
        </div>
      </div>

      <div className="card" style={{ marginTop: '1rem' }}>
        <h2>Recent orders</h2>
        <div className="table-wrap">
          <table className="data">
            <thead>
              <tr>
                <th>Order</th>
                <th>Customer</th>
                <th>Channel</th>
                <th>Total</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {metrics.recent.map((o) => (
                <tr key={o.id}>
                  <td>{o.orderNumber}</td>
                  <td>{o.customerName}</td>
                  <td>{o.channel}</td>
                  <td>{formatMoney(o.total)}</td>
                  <td>{o.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
