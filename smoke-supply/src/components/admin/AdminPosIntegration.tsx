import { useEffect, useState } from 'react';
import { PRODUCTS } from '../../lib/products';
import { getIntegration, loadState } from '../../lib/demo-store';

const DEMO_SKU = 'CIG-RDG-RED-20';

export default function AdminPosIntegration() {
  const [posQty, setPosQty] = useState(0);
  const [webQty, setWebQty] = useState(0);
  const [phase, setPhase] = useState<'idle' | 'pos' | 'integration' | 'website' | 'done'>('idle');
  const [log, setLog] = useState<string[]>([]);
  const [status, setStatus] = useState({
    label: 'Demo Connection — Simulated',
    productsSynced: 0,
    inventoryRecords: 0,
    ordersSynced: 0,
    apiStatus: 'Simulation Active',
    lastSync: null as string | null,
  });
  const [busy, setBusy] = useState(false);

  function refresh() {
    const s = loadState();
    const pos = s.inventory.find((r) => r.sku === DEMO_SKU);
    const web = s.websiteInventory.find((r) => r.sku === DEMO_SKU);
    setPosQty(pos?.quantity ?? 0);
    setWebQty(web?.quantity ?? 0);
    setStatus(getIntegration().pos.getConnectionStatus());
    setLog(s.syncLog.slice(0, 8));
  }

  useEffect(() => {
    refresh();
    window.addEventListener('demo-state-changed', refresh);
    return () => window.removeEventListener('demo-state-changed', refresh);
  }, []);

  async function sleep(ms: number) {
    return new Promise((r) => setTimeout(r, ms));
  }

  async function simulateInStoreSaleAndSync() {
    if (busy) return;
    setBusy(true);
    setPhase('pos');
    const integration = getIntegration();
    integration.pos.recordSale(DEMO_SKU, 2, 'in_store');
    refresh();
    await sleep(700);
    setPhase('integration');
    await sleep(700);
    setPhase('website');
    integration.syncPosToWebsite();
    refresh();
    await sleep(500);
    setPhase('done');
    setBusy(false);
  }

  async function runDemoSync() {
    if (busy) return;
    setBusy(true);
    setPhase('integration');
    await sleep(400);
    setPhase('website');
    getIntegration().syncPosToWebsite();
    refresh();
    await sleep(400);
    setPhase('done');
    setBusy(false);
  }

  const product = PRODUCTS.find((p) => p.sku === DEMO_SKU);

  return (
    <div>
      <p className="notice">
        <strong>SIMULATED POS INTEGRATION</strong> — This does not connect to a real POS. It demonstrates the concept
        using local demo data.
      </p>

      <div className="metric-grid" style={{ marginBottom: '1.25rem' }}>
        <div className="metric">
          <div className="label">Connection</div>
          <div className="value" style={{ fontSize: '1rem' }}>
            {status.label}
          </div>
        </div>
        <div className="metric">
          <div className="label">Last sync</div>
          <div className="value" style={{ fontSize: '1rem' }}>
            {status.lastSync ? 'Just now / recent' : 'Never'}
          </div>
        </div>
        <div className="metric">
          <div className="label">Products synced</div>
          <div className="value">{status.productsSynced} demo</div>
        </div>
        <div className="metric">
          <div className="label">Inventory records</div>
          <div className="value">{status.inventoryRecords} demo</div>
        </div>
        <div className="metric">
          <div className="label">Orders synced</div>
          <div className="value">{status.ordersSynced} demo</div>
        </div>
        <div className="metric">
          <div className="label">API status</div>
          <div className="value" style={{ fontSize: '1rem' }}>
            {status.apiStatus}
          </div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: '1rem' }}>
        <h2>Before / after simulation</h2>
        <p>
          Product: <strong>{product?.name}</strong> ({DEMO_SKU})
        </p>
        <div className="grid-2" style={{ margin: '1rem 0' }}>
          <div className="card" style={{ background: 'var(--paper-2)' }}>
            <h3>Demo POS</h3>
            <p style={{ fontSize: '2rem', fontWeight: 700, margin: 0 }}>{posQty}</p>
            <p style={{ color: 'var(--muted)' }}>Inventory units</p>
          </div>
          <div className="card" style={{ background: 'var(--paper-2)' }}>
            <h3>Website</h3>
            <p style={{ fontSize: '2rem', fontWeight: 700, margin: 0 }}>{webQty}</p>
            <p style={{ color: 'var(--muted)' }}>Shown online</p>
          </div>
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          <button type="button" className="btn btn-primary" disabled={busy} onClick={simulateInStoreSaleAndSync}>
            Simulate: customer buys 2 in store → Sync
          </button>
          <button type="button" className="btn btn-demo" disabled={busy} onClick={runDemoSync}>
            Run Demo Sync
          </button>
        </div>
        <p style={{ marginTop: '0.75rem', fontSize: '0.9rem', color: 'var(--muted)' }}>
          Reverse path: place a storefront pickup order — it flows Website → Integration → POS (see sync log).
        </p>
      </div>

      <div className="sync-viz" aria-live="polite">
        <div className={`sync-node ${phase === 'pos' || phase === 'done' ? 'active' : ''}`}>
          <strong>POS</strong>
          <div>{posQty} units</div>
        </div>
        <div className={`sync-arrow ${phase === 'integration' || phase === 'website' || phase === 'done' ? 'active' : ''}`}>
          → Integration Layer →
        </div>
        <div className={`sync-node ${phase === 'website' || phase === 'done' ? 'active' : ''}`}>
          <strong>Website</strong>
          <div>{webQty} units</div>
        </div>
      </div>

      <div className="card" style={{ marginTop: '1.25rem' }}>
        <h2>Architecture (demo)</h2>
        <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.9rem', lineHeight: 1.5 }}>
{`CUSTOMER
   ↓
WEBSITE
   ↓
ONLINE ORDER
   ↓
INTEGRATION / API LAYER
  ↙                    ↘
POS                    INVENTORY SYSTEM
   ↓
ORDER / INVENTORY / SALES DATA

Exact architecture depends on the real store’s POS and inventory software.`}
        </pre>
      </div>

      <div className="card" style={{ marginTop: '1rem' }}>
        <h2>Sync log</h2>
        <ul>
          {log.map((line, i) => (
            <li key={`${line}-${i}`}>{line}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
