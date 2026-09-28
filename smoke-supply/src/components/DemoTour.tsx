import { useState } from 'react';

const STEPS = [
  {
    title: 'Customer visits website',
    body: 'Start on the homepage. Notice the fictional store branding and pickup CTAs.',
    href: '/',
  },
  {
    title: 'Customer browses products',
    body: 'Open the catalog, search or filter, and open a product detail page.',
    href: '/shop/',
  },
  {
    title: 'Customer places pickup order',
    body: 'Add items to cart and complete demo checkout — pay at pickup or pay online (simulated).',
    href: '/cart/',
  },
  {
    title: 'Store receives order',
    body: 'In the admin Orders list, find the new demo order and change its status.',
    href: '/admin/orders/',
  },
  {
    title: 'POS receives order',
    body: 'Open POS Integration and review the sync log for the online order path.',
    href: '/admin/pos/',
  },
  {
    title: 'Inventory updates',
    body: 'Run “customer buys 2 in store → Sync” to watch POS and website quantities move.',
    href: '/admin/pos/',
  },
  {
    title: 'Stock becomes low',
    body: 'Check Inventory for red/yellow status indicators on demo low-stock SKUs.',
    href: '/admin/inventory/',
  },
  {
    title: 'Reorder indication',
    body: 'Open Reorder Suggestions to see the visible demo formula.',
    href: '/admin/reorder/',
  },
  {
    title: 'Sales & inventory analytics',
    body: 'Finish on Analytics, then Connect Your System for the owner discovery conversation.',
    href: '/admin/analytics/',
  },
] as const;

export default function DemoTour() {
  const [step, setStep] = useState(0);
  const [open, setOpen] = useState(true);
  const current = STEPS[step];

  if (!open) {
    return (
      <button type="button" className="btn btn-demo" onClick={() => setOpen(true)}>
        Resume demo tour
      </button>
    );
  }

  return (
    <div>
      <div className="card" style={{ marginBottom: '1rem' }}>
        <span className="badge badge-demo">DEMO TOUR</span>
        <h1 style={{ marginTop: '0.5rem' }}>Show me how it works</h1>
        <p>A guided walkthrough for store owners. Follow each step on the live demo pages.</p>
        <ol style={{ marginTop: '1rem' }}>
          {STEPS.map((s, i) => (
            <li key={s.title} style={{ marginBottom: '0.45rem', opacity: i === step ? 1 : 0.65 }}>
              <button
                type="button"
                onClick={() => setStep(i)}
                style={{
                  background: 'none',
                  border: 'none',
                  padding: 0,
                  font: 'inherit',
                  cursor: 'pointer',
                  fontWeight: i === step ? 700 : 500,
                  color: 'inherit',
                  textAlign: 'left',
                }}
              >
                {s.title}
              </button>
            </li>
          ))}
        </ol>
      </div>

      <div className={`tour-bar visible`} style={{ position: 'static', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}>
          <div>
            <strong>
              Step {step + 1} / {STEPS.length}: {current.title}
            </strong>
            <p style={{ margin: '0.35rem 0 0', opacity: 0.9 }}>{current.body}</p>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              style={{ color: '#f6f1e8', borderColor: '#445048' }}
              disabled={step === 0}
              onClick={() => setStep((s) => Math.max(0, s - 1))}
            >
              Back
            </button>
            <a className="btn btn-primary btn-sm" href={current.href}>
              Go to step
            </a>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => {
                if (step >= STEPS.length - 1) {
                  window.location.href = '/connect/';
                  return;
                }
                setStep((s) => s + 1);
              }}
            >
              {step >= STEPS.length - 1 ? 'Finish → Connect' : 'Next'}
            </button>
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              style={{ color: '#f6f1e8', borderColor: '#445048' }}
              onClick={() => setOpen(false)}
            >
              Hide
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
