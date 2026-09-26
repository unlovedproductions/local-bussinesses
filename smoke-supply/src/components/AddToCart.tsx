import { useState } from 'react';
import { loadCart, saveCart } from '../lib/demo-store';

interface Props {
  productId: string;
  maxQty?: number;
  label?: string;
}

export default function AddToCart({ productId, maxQty = 20, label = 'Add to cart' }: Props) {
  const [qty, setQty] = useState(1);
  const [msg, setMsg] = useState('');

  function add() {
    const cart = loadCart();
    const existing = cart.find((i) => i.productId === productId);
    if (existing) {
      existing.quantity = Math.min(maxQty, existing.quantity + qty);
    } else {
      cart.push({ productId, quantity: qty });
    }
    saveCart(cart);
    setMsg('Added to cart');
    setTimeout(() => setMsg(''), 2000);
  }

  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', alignItems: 'center' }}>
      <label>
        <span className="visually-hidden">Quantity</span>
        <select
          aria-label="Quantity"
          value={qty}
          onChange={(e) => setQty(Number(e.target.value))}
          style={{ width: '4.5rem' }}
        >
          {Array.from({ length: Math.min(10, maxQty) }, (_, i) => i + 1).map((n) => (
            <option key={n} value={n}>
              {n}
            </option>
          ))}
        </select>
      </label>
      <button type="button" className="btn btn-primary" onClick={add}>
        {label}
      </button>
      {msg ? <span role="status" style={{ color: 'var(--ok)', fontWeight: 600 }}>{msg}</span> : null}
    </div>
  );
}
