import { useEffect, useState } from 'react';
import { loadState } from '../lib/demo-store';
import { stockStatus, statusLabel } from '../lib/inventory-math';

interface Props {
  productId: string;
}

export default function LiveStock({ productId }: Props) {
  const [text, setText] = useState('Checking demo stock…');
  const [cls, setCls] = useState('badge-demo');

  useEffect(() => {
    const refresh = () => {
      const inv = loadState().websiteInventory.find((r) => r.productId === productId);
      if (!inv) {
        setText('Demo stock unavailable');
        setCls('badge-warn');
        return;
      }
      const s = stockStatus(inv);
      setText(`${statusLabel(s)} · ${inv.quantity} available (demo)`);
      setCls(s === 'healthy' ? 'badge-ok' : s === 'low' ? 'badge-warn' : 'badge-danger');
    };
    refresh();
    window.addEventListener('demo-state-changed', refresh);
    return () => window.removeEventListener('demo-state-changed', refresh);
  }, [productId]);

  return <span className={`badge ${cls}`}>{text}</span>;
}
