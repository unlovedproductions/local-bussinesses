import { useEffect, useState } from 'react';
import { loadState } from '../lib/demo-store';
import { formatMoney } from '../lib/inventory-math';
import { STORE } from '../lib/store-info';
import type { DemoOrder } from '../lib/types';

function paymentLabel(order: DemoOrder): string {
  if (order.paymentMethod === 'pay_online') {
    return order.paymentStatus === 'paid_demo' ? 'Paid online (demo — no real charge)' : 'Pay online (pending)';
  }
  return order.paymentStatus === 'paid_demo' ? 'Paid at counter (demo)' : 'Pay at pickup';
}

export default function OrderConfirmation() {
  const [order, setOrder] = useState<DemoOrder | null>(null);
  const [missing, setMissing] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const id = params.get('id');
    if (!id) {
      setMissing(true);
      return;
    }
    const found = loadState().orders.find((o) => o.id === id || o.orderNumber === id);
    if (!found) setMissing(true);
    else setOrder(found);
  }, []);

  if (missing) {
    return (
      <div className="card">
        <h1>Order not found</h1>
        <p>This demo order id is not in local demo storage. Place a new demo order from checkout.</p>
        <a className="btn btn-primary" href="/shop">
          Back to shop
        </a>
      </div>
    );
  }

  if (!order) {
    return <p>Loading demo order…</p>;
  }

  const paidOnline = order.paymentMethod === 'pay_online' && order.paymentStatus === 'paid_demo';

  return (
    <div>
      <div className="notice">
        <strong>DEMO ORDER CONFIRMATION</strong> —{' '}
        {paidOnline
          ? 'Online payment was simulated only; no real charge occurred.'
          : 'Pay-at-pickup selected; no online charge.'}{' '}
        Inventory changes are simulated in browser storage.
      </div>
      <div className="card" style={{ marginTop: '1rem' }}>
        <span className={`badge ${paidOnline ? 'badge-ok' : 'badge-warn'}`}>
          {paidOnline ? 'Paid online (demo)' : 'Pay at pickup'}
        </span>
        <h1 style={{ margin: '0.5rem 0' }}>Thanks, {order.customerName}</h1>
        <p>
          Order <strong>{order.orderNumber}</strong> is queued for in-store pickup.
        </p>
        <p>
          <strong>Payment:</strong> {paymentLabel(order)}
        </p>
        <div className="grid-2" style={{ marginTop: '1.25rem' }}>
          <div>
            <h2>Items</h2>
            <ul>
              {order.items.map((i) => (
                <li key={i.sku}>
                  {i.name} × {i.quantity} — {formatMoney(i.unitPrice * i.quantity)}
                </li>
              ))}
            </ul>
            <p>
              <strong>Total: {formatMoney(order.total)}</strong>
            </p>
          </div>
          <div>
            <h2>Pickup</h2>
            <p>{STORE.address.full}</p>
            <p>{STORE.phone}</p>
            <p>Estimated ready in about {order.estimatedReadyMinutes} minutes during open hours.</p>
            <p>{STORE.pickupHoursNote}</p>
            <ol>
              <li>Bring this order number: <strong>{order.orderNumber}</strong></li>
              <li>Bring a valid photo ID for age verification as required by law and store policy.</li>
              <li>
                {paidOnline
                  ? 'Your demo order is marked paid online — in production, staff would see paid status in POS.'
                  : 'Pay at the counter when you pick up (unless you paid online).'}
              </li>
            </ol>
          </div>
        </div>
        <div className="notice notice-warn" style={{ marginTop: '1rem' }}>
          Production ordering would incorporate the store’s POS, payment processor, inventory system, and applicable
          legal requirements. This page is a concept demonstration.
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '1rem' }}>
          <a className="btn btn-secondary" href="/pickup">
            Pickup instructions
          </a>
          <a className="btn btn-demo" href="/admin/orders">
            View in demo admin
          </a>
          <a className="btn btn-ghost" href="/shop">
            Continue shopping
          </a>
        </div>
      </div>
    </div>
  );
}
