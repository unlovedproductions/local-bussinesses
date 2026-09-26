/** Fictional demo business — not a real store. */
export const STORE = {
  name: 'Smoke & Supply',
  legalName: 'Smoke & Supply Demo LLC (Fictional)',
  tagline: 'Neighborhood tobacco & supply — order online, pick up in store',
  isFictional: true,
  address: {
    street: '1847 Maple Ridge Avenue',
    city: 'Riverbend',
    state: 'OR',
    zip: '97035',
    full: '1847 Maple Ridge Avenue, Riverbend, OR 97035',
  },
  phone: '(555) 014-2837',
  phoneHref: 'tel:+15550142837',
  email: 'hello@smoke-supply-demo.example',
  hours: [
    { day: 'Monday', open: '10:00 AM', close: '8:00 PM' },
    { day: 'Tuesday', open: '10:00 AM', close: '8:00 PM' },
    { day: 'Wednesday', open: '10:00 AM', close: '8:00 PM' },
    { day: 'Thursday', open: '10:00 AM', close: '9:00 PM' },
    { day: 'Friday', open: '10:00 AM', close: '9:00 PM' },
    { day: 'Saturday', open: '10:00 AM', close: '9:00 PM' },
    { day: 'Sunday', open: '11:00 AM', close: '6:00 PM' },
  ],
  pickupHoursNote: 'Pickup available during all open hours. Allow 20–40 minutes for preparation.',
  serviceArea: 'Riverbend and surrounding neighborhoods (demo placeholder)',
  ageNotice:
    'Adults only (21+). This demonstration includes an eligibility notice. It does not perform legal age verification. A production site must follow the store’s jurisdiction, payment rules, and applicable tobacco laws.',
  demoNotice:
    'This is a fictional demonstration website. Store details, products, prices, and inventory are example data — not a real business.',
  taxRate: 0.0,
  mapEmbedLabel: 'Map placeholder — Riverbend, OR (demo location)',
} as const;

export const CATEGORIES = [
  {
    id: 'cigarettes' as const,
    name: 'Cigarettes',
    description: 'Packs and cartons from fictional demo brands',
    complianceNote: 'Age-restricted tobacco product. Production sites require jurisdiction-compliant sale rules.',
  },
  {
    id: 'cigars' as const,
    name: 'Cigars',
    description: 'Machine-made and premium-style demo cigars',
    complianceNote: 'Age-restricted tobacco product.',
  },
  {
    id: 'tobacco' as const,
    name: 'Pipe & RYO Tobacco',
    description: 'Pipe blends and roll-your-own demo pouches',
    complianceNote: 'Age-restricted tobacco product.',
  },
  {
    id: 'nicotine-pouches' as const,
    name: 'Nicotine Pouches',
    description: 'Tobacco-free nicotine pouch demo SKUs',
    complianceNote: 'Age-restricted nicotine product where regulated.',
  },
  {
    id: 'vapes' as const,
    name: 'Vapes & Devices',
    description: 'Demo disposable and device accessories (fictional brands)',
    complianceNote: 'Age-restricted nicotine products. Local regulations vary widely.',
  },
  {
    id: 'accessories' as const,
    name: 'Accessories',
    description: 'Papers, tips, cases, and retail accessories',
  },
  {
    id: 'lighters' as const,
    name: 'Lighters',
    description: 'Disposable and refillable demo lighters',
  },
];

export function categoryById(id: string) {
  return CATEGORIES.find((c) => c.id === id);
}
