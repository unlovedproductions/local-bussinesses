import { useEffect, useState } from 'react';
import { loadCart } from '../lib/demo-store';

export default function CartBadge() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const refresh = () => {
      const items = loadCart();
      setCount(items.reduce((n, i) => n + i.quantity, 0));
    };
    refresh();
    window.addEventListener('cart-changed', refresh);
    window.addEventListener('storage', refresh);
    return () => {
      window.removeEventListener('cart-changed', refresh);
      window.removeEventListener('storage', refresh);
    };
  }, []);

  return (
    <a className="btn btn-primary btn-sm" href="/cart" aria-label={`Cart, ${count} items`}>
      Cart{count > 0 ? ` (${count})` : ''}
    </a>
  );
}
