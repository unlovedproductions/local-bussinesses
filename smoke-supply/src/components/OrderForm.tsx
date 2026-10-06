import { useEffect, useMemo, useState } from 'react';

type Plan = 'half' | 'six' | 'forty' | 'phased';

type PackageOpt = {
  id: string;
  group: string;
  name: string;
  setup: number;
  monthly: number;
  later: number;
  detail: string;
};

type DomainOpt = {
  id: string;
  register: number;
  renew: number;
  note: string;
};

type Line = { label: string; amount: number; note?: string };

const PACKAGES: PackageOpt[] = [
  {
    id: 'essential',
    group: 'Basic website',
    name: 'Essential',
    setup: 1300,
    monthly: 0,
    later: 0,
    detail: 'Home, shop, visit, contact. One design, one revision round.',
  },
  {
    id: 'standard',
    group: 'Basic website',
    name: 'Standard',
    setup: 2100,
    monthly: 0,
    later: 0,
    detail: 'Essential, plus local SEO foundation, demo videos, two revision rounds, two weeks of support.',
  },
  {
    id: 'full',
    group: 'Basic website',
    name: 'Full scope',
    setup: 1300,
    monthly: 0,
    later: 800,
    detail: 'Phase 1 is the Essential site. Phase 2 is the POS and inventory demo, $800 when you start it.',
  },
  {
    id: 'pickup',
    group: 'Retail system',
    name: 'Pickup website',
    setup: 4500,
    monthly: 249,
    later: 0,
    detail: 'Working pickup ordering, staff order board, pay at the counter, email when an order comes in. Up to 150 products.',
  },
  {
    id: 'pos-clean',
    group: 'Retail system',
    name: 'POS + inventory, clean match',
    setup: 9500,
    monthly: 395,
    later: 0,
    detail: 'Pickup site plus a documented POS whose SKUs already match and can take online orders.',
  },
  {
    id: 'pos',
    group: 'Retail system',
    name: 'POS + inventory',
    setup: 12000,
    monthly: 450,
    later: 0,
    detail: 'Pickup site, one POS connection, SKU matching, scheduled stock and prices, sold-out items blocked.',
  },
  {
    id: 'pos-board',
    group: 'Retail system',
    name: 'POS stock, orders stay on the board',
    setup: 15500,
    monthly: 495,
    later: 0,
    detail: 'Stock syncs from the POS. Online orders stay on the staff board because the POS cannot receive them.',
  },
  {
    id: 'pos-hard',
    group: 'Retail system',
    name: 'POS + inventory, difficult setup',
    setup: 17500,
    monthly: 595,
    later: 0,
    detail: 'No sandbox, a slow vendor, or a dirty catalog, and orders still have to land in the POS.',
  },
];

const DASHBOARDS = [
  { id: 'none', name: 'No owner dashboard', setup: 0, monthly: 0, detail: 'Staff order board only.' },
  {
    id: 'simple',
    name: 'Today’s totals + morning email',
    setup: 4000,
    monthly: 150,
    detail: 'Today’s numbers, low-stock count, and a morning email.',
  },
  {
    id: 'mid',
    name: 'Owner dashboard',
    setup: 6000,
    monthly: 200,
    detail: 'Totals, top sellers, a chart, and a reorder list you review. With standard POS this is the $18,000 system.',
  },
  {
    id: 'books',
    name: 'Dashboard matched to the register',
    setup: 9000,
    monthly: 300,
    detail: 'Refunds, discounts, and a comparison against the POS report.',
  },
];

const DOMAINS: DomainOpt[] = [
  { id: 'aliscstore.com', register: 10.98, renew: 18.48, note: 'Closest to Ali’s C Store' },
  { id: 'alis-c-store.com', register: 10.98, renew: 18.48, note: 'Easier to say' },
  { id: 'alis-cstore.com', register: 10.98, renew: 18.48, note: 'Clear when spoken' },
  { id: 'alisctobacco.com', register: 10.98, renew: 18.48, note: 'Says tobacco' },
  { id: 'alissmokeshop.com', register: 10.98, renew: 18.48, note: 'Says smoke shop' },
  { id: 'alissmoke.com', register: 10.98, renew: 18.48, note: 'Short' },
  { id: 'alis-c.com', register: 10.98, renew: 18.48, note: 'Short, harder to guess' },
  { id: 'aliscstore.net', register: 11.98, renew: 15, note: 'Backup only' },
  { id: 'aliscstore.org', register: 8.48, renew: 18.98, note: 'Less typical for a shop' },
  { id: 'aliscstore.shop', register: 0.98, renew: 38.98, note: 'Cheap first year, expensive renewal' },
];

const STORAGE_KEY = 'ali-order-form-v1';

function money(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
}

function domainFee(id: string, promo: boolean): { year1: number; renew: number } | null {
  const domain = DOMAINS.find((d) => d.id === id);
  if (!domain) return null;
  const register = promo && domain.id.endsWith('.com') ? 6.79 : domain.register;
  return { year1: register + 0.2 + 10, renew: domain.renew };
}

function isPos(id: string): boolean {
  return id.startsWith('pos');
}

function isRetail(id: string): boolean {
  return id === 'pickup' || isPos(id);
}

export default function OrderForm() {
  const [pkgId, setPkgId] = useState('');
  const [dashId, setDashId] = useState('none');
  const [primary, setPrimary] = useState('none');
  const [extras, setExtras] = useState<string[]>([]);
  const [promo, setPromo] = useState(false);
  const [hosting, setHosting] = useState(0);
  const [maintenance, setMaintenance] = useState(0);
  const [plan, setPlan] = useState<Plan>('half');
  const [cleanup, setCleanup] = useState(false);
  const [redesign, setRedesign] = useState(false);
  const [cards, setCards] = useState(false);
  const [onsite, setOnsite] = useState(false);
  const [rush, setRush] = useState(false);
  const [extraSkus, setExtraSkus] = useState(0);
  const [descriptions, setDescriptions] = useState(0);
  const [editHours, setEditHours] = useState(0);
  const [storeName, setStoreName] = useState('');
  const [ownerName, setOwnerName] = useState('');
  const [phone, setPhone] = useState('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      const saved = JSON.parse(raw) as Record<string, unknown>;
      if (typeof saved.pkgId === 'string') setPkgId(saved.pkgId);
      if (typeof saved.dashId === 'string') setDashId(saved.dashId);
      if (typeof saved.primary === 'string') setPrimary(saved.primary);
      if (Array.isArray(saved.extras)) setExtras(saved.extras.filter((x) => typeof x === 'string'));
      if (typeof saved.promo === 'boolean') setPromo(saved.promo);
      if (typeof saved.hosting === 'number') setHosting(saved.hosting);
      if (typeof saved.maintenance === 'number') setMaintenance(saved.maintenance);
      if (saved.plan === 'half' || saved.plan === 'six' || saved.plan === 'forty' || saved.plan === 'phased') {
        setPlan(saved.plan);
      } else if (saved.plan === 'four') {
        setPlan('half');
      }
      if (typeof saved.cleanup === 'boolean') setCleanup(saved.cleanup);
      if (typeof saved.redesign === 'boolean') setRedesign(saved.redesign);
      if (typeof saved.cards === 'boolean') setCards(saved.cards);
      if (typeof saved.onsite === 'boolean') setOnsite(saved.onsite);
      if (typeof saved.rush === 'boolean') setRush(saved.rush);
      if (typeof saved.extraSkus === 'number') setExtraSkus(saved.extraSkus);
      if (typeof saved.descriptions === 'number') setDescriptions(saved.descriptions);
      if (typeof saved.editHours === 'number') setEditHours(saved.editHours);
      if (typeof saved.storeName === 'string') setStoreName(saved.storeName);
      if (typeof saved.ownerName === 'string') setOwnerName(saved.ownerName);
      if (typeof saved.phone === 'string') setPhone(saved.phone);
    } catch {
      /* ignore a bad save */
    }
  }, []);

  useEffect(() => {
    if (!isPos(pkgId) && dashId !== 'none') setDashId('none');
    if (!isPos(pkgId) && onsite) setOnsite(false);
    if (!isRetail(pkgId)) {
      if (cleanup) setCleanup(false);
      if (extraSkus !== 0) setExtraSkus(0);
    }
    if (pkgId !== 'full' && plan === 'phased') setPlan('half');
    if (!isRetail(pkgId) && plan === 'forty') setPlan('half');
    if (primary === 'none' || !primary.endsWith('.com')) {
      if (promo) setPromo(false);
    }
    setExtras((current) => {
      const next = current.filter((id) => id !== primary);
      return next.length === current.length ? current : next;
    });
  }, [pkgId, dashId, onsite, cleanup, extraSkus, plan, primary, promo]);

  const quote = useMemo(() => {
    const pkg = PACKAGES.find((p) => p.id === pkgId);
    const dash = isPos(pkgId) ? DASHBOARDS.find((d) => d.id === dashId) ?? DASHBOARDS[0] : DASHBOARDS[0];
    const lines: Line[] = [];
    if (!pkg) {
      return {
        lines,
        setup: 0,
        monthly: 0,
        dueToday: 0,
        remaining: 0,
        renew: 0,
        schedule: 'Choose one package.',
        summary: 'No package selected.',
      };
    }

    lines.push({ label: pkg.name, amount: pkg.setup });
    if (pkg.later > 0) {
      lines.push({
        label: 'Phase 2 — POS and inventory demo',
        amount: pkg.later,
        note: 'Billed when that phase starts, unless the payment plan above spreads it',
      });
    }
    if (dash.setup > 0 || dash.monthly > 0) {
      lines.push({ label: dash.name, amount: dash.setup, note: dash.monthly ? `${money(dash.monthly)}/month` : undefined });
    }

    let labor = pkg.setup + dash.setup;
    if (isRetail(pkgId) && cleanup) {
      lines.push({ label: 'Clean up the product spreadsheet', amount: 750 });
      labor += 750;
    }
    if (redesign) {
      lines.push({ label: 'New visual design', amount: 1200 });
      labor += 1200;
    }
    if (cards) {
      lines.push({ label: 'Online card payment', amount: 1200, note: 'Only if a processor will accept the store' });
      labor += 1200;
    }
    if (isPos(pkgId) && onsite) {
      lines.push({ label: 'On-site test day', amount: 1500 });
      labor += 1500;
    }
    const skuCount = isRetail(pkgId) ? Math.max(0, extraSkus) : 0;
    if (skuCount > 0) {
      const skuTotal = skuCount * 3;
      lines.push({ label: `${skuCount} products past the 150 included`, amount: skuTotal, note: '$3 each' });
      labor += skuTotal;
    }
    const copyCount = Math.max(0, descriptions);
    if (copyCount > 0) {
      const copyTotal = copyCount * 20;
      lines.push({ label: `Write ${copyCount} product descriptions`, amount: copyTotal, note: '$20 each' });
      labor += copyTotal;
    }
    const hours = Math.max(0, editHours);
    if (hours > 0) {
      const hourTotal = hours * 50;
      lines.push({ label: `${hours} extra content hours`, amount: hourTotal, note: '$50/hour' });
      labor += hourTotal;
    }
    const rushAmount = rush ? Math.round(labor * 0.15 * 100) / 100 : 0;
    if (rushAmount > 0) {
      lines.push({ label: 'Rush, under three weeks', amount: rushAmount, note: '15% of the work above' });
    }

    let domainYear1 = 0;
    let renew = 0;
    const primaryFee = primary === 'none' ? null : domainFee(primary, promo);
    if (primaryFee && primary !== 'none') {
      lines.push({
        label: `Domain ${primary}`,
        amount: primaryFee.year1,
        note: `Renews at ${money(primaryFee.renew)}/year, not in this total`,
      });
      domainYear1 += primaryFee.year1;
      renew += primaryFee.renew;
    }
    for (const id of extras) {
      if (id === primary) continue;
      const fee = domainFee(id, false);
      if (!fee) continue;
      lines.push({
        label: `Extra domain ${id}`,
        amount: fee.year1,
        note: `Renews at ${money(fee.renew)}/year`,
      });
      domainYear1 += fee.year1;
      renew += fee.renew;
    }

    const workNow = labor + rushAmount;
    const phased = plan === 'phased' && pkg.later > 0;
    const feeBase = workNow + (phased ? 0 : pkg.later);
    const fee = plan === 'six' ? Math.round(feeBase * 0.05 * 100) / 100 : 0;
    if (fee > 0) lines.push({ label: 'Six-payment fee', amount: fee, note: '5% of the work, not the domain' });

    if (hosting > 0) lines.push({ label: 'Hosting', amount: 0, note: `${money(hosting)}/month, paid to hosting` });
    if (maintenance > 0) {
      lines.push({ label: 'Maintenance after the support window', amount: 0, note: `${money(maintenance)}/month` });
    }

    const payable = workNow + pkg.later + fee + domainYear1;
    let dueToday = payable;
    let schedule = 'Due in full to start.';
    if (plan === 'half') {
      dueToday = payable / 2;
      schedule = `Half before work starts (${money(dueToday)}), half the day it launches (${money(payable - dueToday)}).`;
    } else if (plan === 'six') {
      dueToday = payable / 6;
      schedule = `${money(dueToday)} today, then five monthly payments. Total with the 5% fee is ${money(payable)}.`;
    } else if (plan === 'forty') {
      dueToday = payable * 0.4;
      schedule = `40% today (${money(dueToday)}), 30% when a test sync works, 30% at opening.`;
    } else if (phased) {
      dueToday = workNow + fee + domainYear1;
      schedule = `Phase 1 today (${money(dueToday)}). Phase 2 is ${money(pkg.later)} when you start it.`;
    }

    const setup = payable;
    const monthly = pkg.monthly + dash.monthly + hosting + maintenance;
    const remaining = setup - dueToday;

    const summaryLines = [
      storeName || 'Ali’s C Store',
      ownerName,
      phone,
      '',
      ...lines.map((line) => `${line.label}: ${line.amount ? money(line.amount) : line.note ?? ''}${line.amount && line.note ? ` (${line.note})` : ''}`),
      '',
      `One-time total: ${money(setup)}`,
      `Due today: ${money(dueToday)}`,
      `Still to pay: ${money(remaining)}`,
      `Monthly: ${money(monthly)}`,
      schedule,
      renew ? `Domain renewal next year: ${money(renew)} (not included above)` : '',
    ].filter((line) => line !== undefined);

    return {
      lines,
      setup,
      monthly,
      dueToday,
      remaining,
      renew,
      schedule,
      summary: summaryLines.join('\n'),
    };
  }, [
    pkgId,
    dashId,
    primary,
    extras,
    promo,
    hosting,
    maintenance,
    plan,
    cleanup,
    redesign,
    cards,
    onsite,
    rush,
    extraSkus,
    descriptions,
    editHours,
    storeName,
    ownerName,
    phone,
  ]);

  useEffect(() => {
    const payload = {
      pkgId,
      dashId,
      primary,
      extras,
      promo,
      hosting,
      maintenance,
      plan,
      cleanup,
      redesign,
      cards,
      onsite,
      rush,
      extraSkus,
      descriptions,
      editHours,
      storeName,
      ownerName,
      phone,
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  }, [
    pkgId,
    dashId,
    primary,
    extras,
    promo,
    hosting,
    maintenance,
    plan,
    cleanup,
    redesign,
    cards,
    onsite,
    rush,
    extraSkus,
    descriptions,
    editHours,
    storeName,
    ownerName,
    phone,
  ]);

  function toggleExtra(id: string) {
    setExtras((current) => (current.includes(id) ? current.filter((item) => item !== id) : [...current, id]));
  }

  async function copySummary() {
    try {
      await navigator.clipboard.writeText(quote.summary);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  }

  const groups = [...new Set(PACKAGES.map((pkg) => pkg.group))];

  return (
    <form className="order-form" onSubmit={(event) => event.preventDefault()}>
      <fieldset>
        <legend>Your name</legend>
        <label>
          Store name
          <input value={storeName} onChange={(event) => setStoreName(event.target.value)} autoComplete="organization" />
        </label>
        <label>
          Your name
          <input value={ownerName} onChange={(event) => setOwnerName(event.target.value)} autoComplete="name" />
        </label>
        <label>
          Mobile number
          <input value={phone} onChange={(event) => setPhone(event.target.value)} type="tel" inputMode="tel" autoComplete="tel" />
        </label>
      </fieldset>

      <fieldset>
        <legend>Package — pick one</legend>
        <p className="order-help">The basic website and the retail system are different starting points. The total uses the one you select.</p>
        {groups.map((group) => (
          <div key={group}>
            <h2>{group}</h2>
            {PACKAGES.filter((pkg) => pkg.group === group).map((pkg) => (
              <label key={pkg.id} className={pkgId === pkg.id ? 'choice on' : 'choice'}>
                <input type="radio" name="package" checked={pkgId === pkg.id} onChange={() => setPkgId(pkg.id)} />
                <span>
                  <strong>
                    {pkg.name} · {money(pkg.setup)}
                    {pkg.later > 0 ? ` now + ${money(pkg.later)} later` : ''}
                    {pkg.monthly > 0 ? ` + ${money(pkg.monthly)}/mo` : ''}
                  </strong>
                  <small>{pkg.detail}</small>
                </span>
              </label>
            ))}
          </div>
        ))}
      </fieldset>

      {isPos(pkgId) ? (
        <fieldset>
          <legend>Owner dashboard — pick one</legend>
          {DASHBOARDS.map((dash) => (
            <label key={dash.id} className={dashId === dash.id ? 'choice on' : 'choice'}>
              <input type="radio" name="dashboard" checked={dashId === dash.id} onChange={() => setDashId(dash.id)} />
              <span>
                <strong>
                  {dash.name}
                  {dash.setup > 0 ? ` · +${money(dash.setup)} + ${money(dash.monthly)}/mo` : ' · included'}
                </strong>
                <small>{dash.detail}</small>
              </span>
            </label>
          ))}
        </fieldset>
      ) : null}

      <fieldset>
        <legend>Add-ons</legend>
        {isRetail(pkgId) ? (
          <label className={cleanup ? 'choice on' : 'choice'}>
            <input type="checkbox" checked={cleanup} onChange={(event) => setCleanup(event.target.checked)} />
            <span>
              <strong>Clean up the product spreadsheet · $750</strong>
              <small>Missing SKUs, prices, or categories.</small>
            </span>
          </label>
        ) : null}
        <label className={redesign ? 'choice on' : 'choice'}>
          <input type="checkbox" checked={redesign} onChange={(event) => setRedesign(event.target.checked)} />
          <span>
            <strong>New visual design · $1,200</strong>
            <small>A new look, instead of restyling the current demo.</small>
          </span>
        </label>
        <label className={cards ? 'choice on' : 'choice'}>
          <input type="checkbox" checked={cards} onChange={(event) => setCards(event.target.checked)} />
          <span>
            <strong>Online card payment · $1,200</strong>
            <small>Only after a processor agrees to take this store.</small>
          </span>
        </label>
        {isPos(pkgId) ? (
          <label className={onsite ? 'choice on' : 'choice'}>
            <input type="checkbox" checked={onsite} onChange={(event) => setOnsite(event.target.checked)} />
            <span>
              <strong>On-site test day · $1,500</strong>
              <small>One day in the store proving the sync.</small>
            </span>
          </label>
        ) : null}
        <label className={rush ? 'choice on' : 'choice'}>
          <input type="checkbox" checked={rush} onChange={(event) => setRush(event.target.checked)} />
          <span>
            <strong>Live in under three weeks · +15%</strong>
            <small>Applied to the work above, not to the domain.</small>
          </span>
        </label>
        {isRetail(pkgId) ? (
          <label>
            Products beyond the 150 included · $3 each
            <input
              type="number"
              inputMode="numeric"
              min={0}
              max={2000}
              value={extraSkus}
              onChange={(event) => setExtraSkus(Number(event.target.value) || 0)}
            />
          </label>
        ) : null}
        <label>
          Product descriptions for me to write · $20 each
          <input
            type="number"
            inputMode="numeric"
            min={0}
            max={500}
            value={descriptions}
            onChange={(event) => setDescriptions(Number(event.target.value) || 0)}
          />
        </label>
        <label>
          Extra content hours · $50/hour
          <input
            type="number"
            inputMode="numeric"
            min={0}
            max={80}
            value={editHours}
            onChange={(event) => setEditHours(Number(event.target.value) || 0)}
          />
        </label>
      </fieldset>

      <fieldset>
        <legend>Domain — pick the main name</legend>
        <label className={primary === 'none' ? 'choice on' : 'choice'}>
          <input type="radio" name="domain" checked={primary === 'none'} onChange={() => setPrimary('none')} />
          <span>
            <strong>I already have a domain · $0</strong>
          </span>
        </label>
        {DOMAINS.map((domain) => {
          const fee = domainFee(domain.id, promo && domain.id === primary);
          return (
            <label key={domain.id} className={primary === domain.id ? 'choice on' : 'choice'}>
              <input type="radio" name="domain" checked={primary === domain.id} onChange={() => setPrimary(domain.id)} />
              <span>
                <strong>
                  {domain.id} · {fee ? money(fee.year1) : ''}
                </strong>
                <small>
                  {domain.note}. Year 1 includes registration, a $0.20 ICANN fee, and $10 setup. Renews at {money(domain.renew)}
                  /year.
                </small>
              </span>
            </label>
          );
        })}
        <label className={promo ? 'choice on' : 'choice'}>
          <input
            type="checkbox"
            checked={promo}
            disabled={primary === 'none' || !primary.endsWith('.com')}
            onChange={(event) => setPromo(event.target.checked)}
          />
          <span>
            <strong>New Namecheap customer · .com year 1 drops to $6.79</strong>
            <small>Promo NEWCOM679. Applies to the main .com only. Confirm it still exists at signup.</small>
          </span>
        </label>
        <h2>Also register these</h2>
        {DOMAINS.filter((domain) => domain.id !== primary).map((domain) => {
          const fee = domainFee(domain.id, false);
          const on = extras.includes(domain.id);
          return (
            <label key={domain.id} className={on ? 'choice on' : 'choice'}>
              <input type="checkbox" checked={on} onChange={() => toggleExtra(domain.id)} />
              <span>
                <strong>
                  {domain.id} · {fee ? money(fee.year1) : ''}
                </strong>
                <small>Redirects to the main name. Renews at {money(domain.renew)}/year.</small>
              </span>
            </label>
          );
        })}
      </fieldset>

      <fieldset>
        <legend>Monthly costs — pick one of each</legend>
        <h2>Hosting</h2>
        {[0, 25, 30, 35].map((amount) => (
          <label key={amount} className={hosting === amount ? 'choice on' : 'choice'}>
            <input type="radio" name="hosting" checked={hosting === amount} onChange={() => setHosting(amount)} />
            <span>
              <strong>{amount === 0 ? 'Already have hosting · $0' : `${money(amount)}/month`}</strong>
            </span>
          </label>
        ))}
        <h2>Maintenance after support ends</h2>
        {[0, 60, 75, 90].map((amount) => (
          <label key={amount} className={maintenance === amount ? 'choice on' : 'choice'}>
            <input type="radio" name="maintenance" checked={maintenance === amount} onChange={() => setMaintenance(amount)} />
            <span>
              <strong>{amount === 0 ? 'No maintenance plan · $0' : `${money(amount)}/month`}</strong>
            </span>
          </label>
        ))}
      </fieldset>

      <fieldset>
        <legend>How to pay the one-time total</legend>
        <label className={plan === 'half' ? 'choice on' : 'choice'}>
          <input type="radio" name="plan" checked={plan === 'half'} onChange={() => setPlan('half')} />
          <span>
            <strong>Half before work starts, half the day it launches</strong>
            <small>No extra fee. Nothing on the setup is due after launch.</small>
          </span>
        </label>
        <label className={plan === 'six' ? 'choice on' : 'choice'}>
          <input type="radio" name="plan" checked={plan === 'six'} onChange={() => setPlan('six')} />
          <span>
            <strong>Six monthly payments · +5%</strong>
            <small>On a $2,100 site with nothing else added, this is $2,205, or $367.50 a month.</small>
          </span>
        </label>
        {isRetail(pkgId) ? (
          <label className={plan === 'forty' ? 'choice on' : 'choice'}>
            <input type="radio" name="plan" checked={plan === 'forty'} onChange={() => setPlan('forty')} />
            <span>
              <strong>40% to start, 30% at a working test, 30% at opening</strong>
              <small>For the POS and pickup systems. No extra fee.</small>
            </span>
          </label>
        ) : null}
        {pkgId === 'full' ? (
          <label className={plan === 'phased' ? 'choice on' : 'choice'}>
            <input type="radio" name="plan" checked={plan === 'phased'} onChange={() => setPlan('phased')} />
            <span>
              <strong>Phase 1 now, phase 2 when ready</strong>
              <small>$1,300 for the site now. The $800 POS demo waits.</small>
            </span>
          </label>
        ) : null}
      </fieldset>

      <section className="order-lines" aria-live="polite">
        <h2>Selected</h2>
        {quote.lines.length === 0 ? <p>Nothing selected yet.</p> : null}
        <ul>
          {quote.lines.map((line) => (
            <li key={line.label}>
              <span>{line.label}</span>
              <span>{line.amount ? money(line.amount) : line.note}</span>
              {line.amount && line.note ? <small>{line.note}</small> : null}
            </li>
          ))}
        </ul>
        <p>{quote.schedule}</p>
        {quote.renew > 0 ? <p>Domain renewal next year, not in today’s total: {money(quote.renew)}.</p> : null}
        <button type="button" className="btn btn-secondary" onClick={copySummary}>
          {copied ? 'Copied' : 'Copy this order'}
        </button>
        <a className="btn btn-ghost" href={`sms:?&body=${encodeURIComponent(quote.summary)}`}>
          Text this order
        </a>
      </section>

      <div className="order-dock" aria-live="polite">
        <div>
          <span>Due today</span>
          <strong>{money(quote.dueToday)}</strong>
        </div>
        <div>
          <span>One-time</span>
          <strong>{money(quote.setup)}</strong>
        </div>
        <div>
          <span>Monthly</span>
          <strong>{money(quote.monthly)}</strong>
        </div>
      </div>
    </form>
  );
}
