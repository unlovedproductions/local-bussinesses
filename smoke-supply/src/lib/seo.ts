import { STORE } from './store-info';

export function localBusinessJsonLd() {
  return {
    '@context': 'https://schema.org',
    '@type': 'LocalBusiness',
    name: STORE.name,
    description: `${STORE.tagline}. Fictional demonstration business — not a real store.`,
    url: 'https://smoke-supply-demo.example.com/',
    telephone: STORE.phone,
    email: STORE.email,
    address: {
      '@type': 'PostalAddress',
      streetAddress: STORE.address.street,
      addressLocality: STORE.address.city,
      addressRegion: STORE.address.state,
      postalCode: STORE.address.zip,
      addressCountry: 'US',
    },
    openingHoursSpecification: STORE.hours.map((h) => ({
      '@type': 'OpeningHoursSpecification',
      dayOfWeek: h.day,
      opens: h.open,
      closes: h.close,
    })),
    additionalProperty: {
      '@type': 'PropertyValue',
      name: 'DemoNotice',
      value: 'Fictional example business for demonstration only',
    },
  };
}

export function faqJsonLd() {
  const faqs = [
    {
      q: 'Does the store offer in-store pickup?',
      a: 'Yes. Smoke & Supply (demo) offers online ordering for in-store pickup during open hours.',
    },
    {
      q: 'What are the store hours?',
      a: 'Demo hours are typically 10 AM–8 PM weekdays, later on Friday–Saturday, and 11 AM–6 PM Sunday. See the Visit page for the full schedule.',
    },
    {
      q: 'Where is the store located?',
      a: `The fictional demo address is ${STORE.address.full}.`,
    },
    {
      q: 'How does online pickup work?',
      a: 'Browse products, place a demo pickup order, wait for preparation, then pick up in store with your order number. Bring valid ID for age verification as required by law and store policy.',
    },
    {
      q: 'What should I bring when picking up my order?',
      a: 'Bring your order number, a valid photo ID, and payment if you chose pay at pickup. Online-paid demo orders only need order number and ID. This demo does not process real payments.',
    },
    {
      q: 'Can I pay online for pickup orders?',
      a: 'Yes in this demo. Choose pay online or pay at pickup at checkout. Online payment is simulated; production would use the store’s payment processor.',
    },
  ];
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map((f) => ({
      '@type': 'Question',
      name: f.q,
      acceptedAnswer: { '@type': 'Answer', text: f.a },
    })),
  };
}
