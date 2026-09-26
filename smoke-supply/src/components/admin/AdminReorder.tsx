import { useEffect, useState } from 'react';
import { PRODUCTS } from '../../lib/products';
import { loadState } from '../../lib/demo-store';
import { stockStatus, suggestedReorderQty } from '../../lib/inventory-math';
import type { InventoryRecord } from '../../lib/types';

export default function AdminReorder() {
  const [rows, setRows] = useState<InventoryRecord[]>([]);

  useEffect(() => {
    const refresh = () => setRows(loadState().inventory.filter((r) => stockStatus(r) !== 'healthy'));
    refresh();
    window.addEventListener('demo-state-changed', refresh);
    return () => window.removeEventListener('demo-state-changed', refresh);
  }, []);

  return (
    <div>
      <div className="notice notice-warn">
        <strong>Demo assumption — not a universal formula.</strong>
        <br />
        Suggested reorder ≈ (daily velocity × lead time) + max(0, minimum − current) + (daily velocity × 3 day
        buffer). Real stores use their own rules and supplier data.
      </div>
      <div className="table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Product</th>
              <th>Current</th>
              <th>Minimum</th>
              <th>Velocity / day</th>
              <th>Lead time (days)</th>
              <th>Suggested reorder</th>
              <th>Supplier</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => {
              const product = PRODUCTS.find((p) => p.id === r.productId);
              return (
                <tr key={r.sku}>
                  <td>{product?.name ?? r.sku}</td>
                  <td>{r.quantity}</td>
                  <td>{r.minimum}</td>
                  <td>{r.dailyVelocity}</td>
                  <td>{r.leadTimeDays}</td>
                  <td>
                    <strong>{suggestedReorderQty(r)}</strong>
                  </td>
                  <td>{r.supplier}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
