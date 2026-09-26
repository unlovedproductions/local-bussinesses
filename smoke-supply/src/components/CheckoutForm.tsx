import { useEffect, useMemo, useState, type FormEvent } from 'react';
import { customAlphabet } from 'nanoid';
import { getProductById } from '../lib/products';
import { getIntegration, loadCart, saveCart, loadState, updateState } from '../lib/demo-store';
import { formatMoney } from '../lib/inventory-math';
import { STORE } from '../lib/store-info';
import type { CartItem, DemoOrder, PaymentMethod } from '../lib/types';

const orderId = customAlphabet('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', 5);

function digitsOnly(value: string): string {
  return value.replace(/\D/g, '');
}

function formatCardNumber(value: string): string {
  return digitsOnly(value)
    .slice(0, 16)
    .replace(/(\d{4})(?=\d)/g, '$1 ')
    .trim();
}

export default function CheckoutForm() {
  const [items, setItems] = useState<CartItem[]>([]);
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [notes, setNotes] = useState('');
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>('pay_at_pickup');
  const [cardName, setCardName] = useState('');
  const [cardNumber, setCardNumber] = useState('');
  const [cardExpiry, setCardExpiry] = useState('');
  const [cardCvc, setCardCvc] = useState('');
  const [agreed, setAgreed] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    setItems(loadCart());
  }, []);

  const lines = useMemo(() => {
    return items
      .map((item) => {
        const product = getProductById(item.productId);
        if (!product) return null;
        return {
          product,
          quantity: item.quantity,
          unitPrice: product.price,
          lineTotal: product.price * item.quantity,
        };
      })
      .filter(Boolean) as {
      product: NonNullable<ReturnType<typeof getProductById>>;
      quantity: number;
      unitPrice: number;
      lineTotal: number;
    }[];
  }, [items]);

  const subtotal = lines.reduce((n, l) => n + l.lineTotal, 0);

  function validateDemoCard(): string | null {
    if (!cardName.trim()) return 'Enter the name on the demo card.';
    const number = digitsOnly(cardNumber);
    if (number.length < 13 || number.length > 16) return 'Enter a demo card number (13–16 digits). Nothing is charged.';
    if (!/^\d{2}\/\d{2}$/.test(cardExpiry.trim())) return 'Enter expiry as MM/YY.';
    if (digitsOnly(cardCvc).length < 3) return 'Enter a demo CVC (3–4 digits).';
    return null;
  }

  function placeOrder(e: FormEvent) {
    e.preventDefault();
    setError('');
    if (!lines.length) {
      setError('Your cart is empty.');
      return;
    }
    if (!name.trim() || !phone.trim()) {
      setError('Name and phone are required for pickup.');
      return;
    }
    if (paymentMethod === 'pay_online') {
      const cardError = validateDemoCard();
      if (cardError) {
        setError(cardError);
        return;
      }
    }
    if (!agreed) {
      setError('Confirm you understand this is a demo order and no real payment is processed.');
      return;
    }

    const state = loadState();
    const orderNumber = `SS-${10050 + state.orders.length}`;
    const paidOnline = paymentMethod === 'pay_online';
    const order: DemoOrder = {
      id: `ord-${orderId()}`,
      orderNumber,
      createdAt: new Date().toISOString(),
      status: 'pending',
      channel: 'online',
      customerName: name.trim(),
      customerPhone: phone.trim(),
      customerEmail: email.trim() || 'demo@example.com',
      items: lines.map((l) => ({
        productId: l.product.id,
        name: l.product.name,
        sku: l.product.sku,
        quantity: l.quantity,
        unitPrice: l.unitPrice,
      })),
      subtotal,
      tax: 0,
      total: subtotal,
      pickupNotes: notes.trim() || undefined,
      estimatedReadyMinutes: 25,
      paymentMethod,
      paymentStatus: paidOnline ? 'paid_demo' : 'unpaid',
    };

    // Demo card fields are never written to storage.
    setCardNumber('');
    setCardCvc('');
    setCardExpiry('');
    setCardName('');

    const integration = getIntegration();
    integration.placeOnlineOrder(order);

    updateState((s) => {
      const existing = s.customers.find(
        (c) => c.phone === order.customerPhone || c.email === order.customerEmail,
      );
      const customers = existing
        ? s.customers.map((c) =>
            c.id === existing.id ? { ...c, orderCount: c.orderCount + 1, name: order.customerName } : c,
          )
        : [
            {
              id: `cust-${orderId()}`,
              name: order.customerName,
              phone: order.customerPhone,
              email: order.customerEmail,
              orderCount: 1,
            },
            ...s.customers,
          ];
      return { ...s, customers };
    });

    saveCart([]);
    window.location.href = `/orders/?id=${encodeURIComponent(order.id)}`;
  }

  if (!lines.length) {
    return (
      <div className="card">
        <p>Nothing to check out. Add products to your demo cart first.</p>
        <a className="btn btn-primary" href="/shop" style={{ marginTop: '0.75rem' }}>
          Shop products
        </a>
      </div>
    );
  }

  return (
    <form onSubmit={placeOrder} className="grid-2" style={{ alignItems: 'start' }}>
      <div className="card">
        <span className="badge badge-demo">Demo checkout — no real charges</span>
        <h2 style={{ marginTop: '0.75rem' }}>Pickup details</h2>
        <p style={{ color: 'var(--muted)', fontSize: '0.92rem' }}>
          Choose pay at pickup or pay online. Online payment is simulated for this demo. Production would use the
          store’s real payment processor.
        </p>
        <div className="form-grid" style={{ marginTop: '1rem' }}>
          <label>
            Full name
            <input required value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" />
          </label>
          <label>
            Phone
            <input required value={phone} onChange={(e) => setPhone(e.target.value)} autoComplete="tel" />
          </label>
          <label>
            Email {paymentMethod === 'pay_online' ? '' : '(optional)'}
            <input
              type="email"
              required={paymentMethod === 'pay_online'}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />
          </label>
          <label>
            Pickup notes (optional)
            <textarea rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} />
          </label>
          <fieldset style={{ border: '1px solid var(--line)', borderRadius: 10, padding: '0.85rem' }}>
            <legend style={{ fontWeight: 700 }}>Fulfillment</legend>
            <label style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', fontWeight: 500 }}>
              <input type="radio" checked readOnly />
              In-store pickup — {STORE.address.full}
            </label>
          </fieldset>
          <fieldset style={{ border: '1px solid var(--line)', borderRadius: 10, padding: '0.85rem' }}>
            <legend style={{ fontWeight: 700 }}>Payment</legend>
            <label style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-start', fontWeight: 500, marginBottom: '0.65rem' }}>
              <input
                type="radio"
                name="paymentMethod"
                checked={paymentMethod === 'pay_at_pickup'}
                onChange={() => setPaymentMethod('pay_at_pickup')}
              />
              <span>
                <strong>Pay at pickup</strong>
                <br />
                <span style={{ color: 'var(--muted)', fontWeight: 400 }}>Pay at the counter when you collect your order.</span>
              </span>
            </label>
            <label style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-start', fontWeight: 500 }}>
              <input
                type="radio"
                name="paymentMethod"
                checked={paymentMethod === 'pay_online'}
                onChange={() => setPaymentMethod('pay_online')}
              />
              <span>
                <strong>Pay online now</strong>
                <br />
                <span style={{ color: 'var(--muted)', fontWeight: 400 }}>
                  Demo card form — no charge is sent to a processor.
                </span>
              </span>
            </label>
          </fieldset>

          {paymentMethod === 'pay_online' ? (
            <fieldset
              style={{ border: '1px solid var(--line)', borderRadius: 10, padding: '0.85rem' }}
              aria-describedby="demo-card-notice"
            >
              <legend style={{ fontWeight: 700 }}>Demo card details</legend>
              <p id="demo-card-notice" className="notice" style={{ marginTop: 0 }}>
                Simulated payment only. Card fields are not stored and are not sent to any payment API. Do not use a
                real card.
              </p>
              <div className="form-grid">
                <label>
                  Name on card
                  <input
                    value={cardName}
                    onChange={(e) => setCardName(e.target.value)}
                    autoComplete="off"
                    data-lpignore="true"
                  />
                </label>
                <label>
                  Card number
                  <input
                    inputMode="numeric"
                    value={cardNumber}
                    onChange={(e) => setCardNumber(formatCardNumber(e.target.value))}
                    placeholder="4242 4242 4242 4242"
                    autoComplete="off"
                    data-lpignore="true"
                  />
                </label>
                <div className="grid-2" style={{ gap: '0.65rem' }}>
                  <label>
                    Expiry (MM/YY)
                    <input
                      value={cardExpiry}
                      onChange={(e) => {
                        let v = digitsOnly(e.target.value).slice(0, 4);
                        if (v.length > 2) v = `${v.slice(0, 2)}/${v.slice(2)}`;
                        setCardExpiry(v);
                      }}
                      placeholder="12/28"
                      autoComplete="off"
                      data-lpignore="true"
                    />
                  </label>
                  <label>
                    CVC
                    <input
                      inputMode="numeric"
                      value={cardCvc}
                      onChange={(e) => setCardCvc(digitsOnly(e.target.value).slice(0, 4))}
                      placeholder="123"
                      autoComplete="off"
                      data-lpignore="true"
                    />
                  </label>
                </div>
              </div>
            </fieldset>
          ) : null}

          <label style={{ display: 'flex', gap: '0.55rem', alignItems: 'flex-start', fontWeight: 500 }}>
            <input type="checkbox" checked={agreed} onChange={(e) => setAgreed(e.target.checked)} />
            <span>
              I understand this is a demonstration order. No real payment is processed
              {paymentMethod === 'pay_online' ? ' even if I choose pay online' : ''}. Age eligibility would be verified
              in a real purchase according to applicable law and store policy.
            </span>
          </label>
          {error ? (
            <p className="notice notice-danger" role="alert">
              {error}
            </p>
          ) : null}
          <button type="submit" className="btn btn-primary">
            {paymentMethod === 'pay_online' ? 'Pay online & place demo order' : 'Place demo order (pay at pickup)'}
          </button>
        </div>
      </div>
      <aside className="card">
        <h2>Order review</h2>
        <ul style={{ listStyle: 'none', padding: 0, margin: '1rem 0' }}>
          {lines.map((l) => (
            <li
              key={l.product.id}
              style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', marginBottom: '0.65rem' }}
            >
              <span>
                {l.product.name} × {l.quantity}
              </span>
              <strong>{formatMoney(l.lineTotal)}</strong>
            </li>
          ))}
        </ul>
        <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--line)', paddingTop: '0.75rem' }}>
          <span>Total (demo)</span>
          <strong>{formatMoney(subtotal)}</strong>
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--muted)', marginTop: '0.85rem' }}>
          Payment: {paymentMethod === 'pay_online' ? 'Pay online (demo)' : 'Pay at pickup'}
        </p>
        <p style={{ fontSize: '0.85rem', color: 'var(--muted)', marginTop: '0.35rem' }}>
          Estimated preparation: about 25 minutes during open hours.
        </p>
      </aside>
    </form>
  );
}
