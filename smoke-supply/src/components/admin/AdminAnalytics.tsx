import { useEffect, useMemo, useState } from 'react';
import { PRODUCTS } from '../../lib/products';
import { loadState } from '../../lib/demo-store';
import { formatMoney, stockStatus } from '../../lib/inventory-math';
import type { DemoState } from '../../lib/types';

export default function AdminAnalytics() {
  const [state, setState] = useState<DemoState | null>(null);
  useEffect(() => setState(loadState()), []);

  const chart = useMemo(() => {
    if (!state) return null;
    const byDay = new Map<string, { online: number; store: number }>();
    for (let i = 13; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      byDay.set(d.toISOString().slice(0, 10), { online: 0, store: 0 });
    }
    for (const s of state.sales) {
      const key = s.date.slice(0, 10);
      const row = byDay.get(key);
      if (!row) continue;
      if (s.channel === 'online') row.online += s.revenue;
      else row.store += s.revenue;
    }
    const days = [...byDay.entries()];
    const max = Math.max(1, ...days.flatMap(([, v]) => [v.online, v.store]));
    const top = new Map<string, number>();
    for (const s of state.sales) top.set(s.productId, (top.get(s.productId) ?? 0) + s.quantity);
    const topList = [...top.entries()]
      .sort((a, b) => b[1] - a[1])
      .slice(0, 6)
      .map(([id, qty]) => ({ name: PRODUCTS.find((p) => p.id === id)?.name ?? id, qty }));
    const low = state.inventory.filter((r) => stockStatus(r) !== 'healthy').length;
    const onlineOrders = state.orders.filter((o) => o.channel === 'online').length;
    const storeOrders = state.orders.filter((o) => o.channel === 'in_store').length;
    return { days, max, topList, low, onlineOrders, storeOrders };
  }, [state]);

  if (!chart) return <p>Loading demo analytics…</p>;

  const w = 640;
  const h = 220;
  const pad = 24;

  return (
    <div>
      <p className="notice">
        <strong>Demo Data</strong> — charts are illustrative fiction for the owner presentation.
      </p>
      <div className="card">
        <h2>Sales over time (demo)</h2>
        <svg viewBox={`0 0 ${w} ${h}`} width="100%" role="img" aria-label="Demo sales chart">
          {chart.days.map(([day, v], i) => {
            const x = pad + (i * (w - pad * 2)) / Math.max(1, chart.days.length - 1);
            const onlineH = (v.online / chart.max) * (h - pad * 2);
            const storeH = (v.store / chart.max) * (h - pad * 2);
            return (
              <g key={day}>
                <rect x={x - 6} y={h - pad - storeH} width={6} height={storeH} fill="#2f4a3c" />
                <rect x={x + 1} y={h - pad - onlineH} width={6} height={onlineH} fill="#b54a2a" />
              </g>
            );
          })}
          <text x={pad} y={16} fill="#6b726c" fontSize="12">
            Green = in-store · Ember = online · Demo Data
          </text>
        </svg>
      </div>

      <div className="grid-2" style={{ marginTop: '1rem' }}>
        <div className="card">
          <h2>Top products</h2>
          <ul>
            {chart.topList.map((t) => (
              <li key={t.name}>
                {t.name}: {t.qty} units
              </li>
            ))}
          </ul>
        </div>
        <div className="card">
          <h2>Channel & stock</h2>
          <p>Online orders (demo): {chart.onlineOrders}</p>
          <p>In-store orders (demo): {chart.storeOrders}</p>
          <p>Low / reorder SKUs: {chart.low}</p>
          <p>
            Sample revenue total:{' '}
            {formatMoney(state!.sales.reduce((n, s) => n + s.revenue, 0))}
          </p>
        </div>
      </div>
    </div>
  );
}
