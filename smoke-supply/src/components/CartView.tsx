import { useEffect, useMemo, useState } from 'react';
import { getProductById } from '../lib/products';
import { loadCart, saveCart } from '../lib/demo-store';
import { formatMoney } from '../lib/inventory-math';
import type { CartItem } from '../lib/types';
import ProductArt from './ProductArt';

export default function CartView() {
  const [items, setItems] = useState<CartItem[]>([]);

  useEffect(() => {
    setItems(loadCart());
  }, []);

  const lines = useMemo(
    () =>
      items
        .map((item) => {
          const product = getProductById(item.productId);
          if (!product) return null;
          return { item, product, lineTotal: product.price * item.quantity };
        })
        .filter(Boolean) as { item: CartItem; product: NonNullable<ReturnType<typeof getProductById>>; lineTotal: number }[],
    [items],
  );

  const subtotal = lines.reduce((n, l) => n + l.lineTotal, 0);

  function updateQty(productId: string, quantity: number) {
    const next =
      quantity <= 0
        ? items.filter((i) => i.productId !== productId)
        : items.map((i) => (i.productId === productId ? { ...i, quantity } : i));
    setItems(next);
    saveCart(next);
  }

  if (lines.length === 0) {
    return (
      <div className="card">
        <p>Your demo cart is empty.</p>
        <p style={{ marginTop: '0.75rem' }}>
          <a className="btn btn-primary" href="/shop">
            Browse products
          </a>
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="notice">
        Demo cart. At checkout you can choose pay at pickup or pay online — both are simulated; no real charge.
      </div>
      <div className="table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Product</th>
              <th>Price</th>
              <th>Qty</th>
              <th>Total</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {lines.map(({ item, product, lineTotal }) => (
              <tr key={product.id}>
                <td>
                  <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                    <ProductArt product={product} size={48} />
                    <div>
                      <strong>{product.name}</strong>
                      <div style={{ fontSize: '0.8rem', color: 'var(--muted)' }}>{product.sku}</div>
                    </div>
                  </div>
                </td>
                <td>{formatMoney(product.price)}</td>
                <td>
                  <input
                    type="number"
                    min={1}
                    max={20}
                    value={item.quantity}
                    aria-label={`Quantity for ${product.name}`}
                    style={{ width: '4.5rem' }}
                    onChange={(e) => updateQty(product.id, Number(e.target.value))}
                  />
                </td>
                <td>{formatMoney(lineTotal)}</td>
                <td>
                  <button type="button" className="btn btn-ghost btn-sm" onClick={() => updateQty(product.id, 0)}>
                    Remove
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <strong style={{ fontSize: '1.2rem' }}>Subtotal: {formatMoney(subtotal)}</strong>
        <a className="btn btn-primary" href="/checkout">
          Proceed to demo checkout
        </a>
      </div>
    </div>
  );
}
