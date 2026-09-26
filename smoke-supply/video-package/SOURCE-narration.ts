export const SCENES = [
  {
    id: 1,
    title: 'Customer Orders',
    caption: 'A customer visits the website and orders products for pickup.',
    narration:
      'A customer opens the Smoke and Supply website, browses the catalog, and places an order for in-store pickup.',
  },
  {
    id: 2,
    title: 'Order Reaches Store',
    caption: 'The website sends the order into an integration layer.',
    narration:
      'Instead of stopping at the website, the order is handed to an integration layer that can talk to the store’s existing systems.',
  },
  {
    id: 3,
    title: 'POS',
    caption: 'The simulated POS receives the order.',
    narration:
      'The point-of-sale system receives the online order so staff can prepare it alongside normal counter activity.',
  },
  {
    id: 4,
    title: 'Inventory',
    caption: 'Inventory updates automatically in the simulation.',
    narration:
      'Inventory counts adjust when the online order is accepted, reducing the risk of showing items that are no longer available.',
  },
  {
    id: 5,
    title: 'In-Store Sale',
    caption: 'A simulated in-store sale also reduces inventory.',
    narration:
      'When a walk-in customer buys the same product at the counter, the POS inventory drops again.',
  },
  {
    id: 6,
    title: 'Website Updates',
    caption: 'After sync, the website reflects the updated inventory.',
    narration:
      'A synchronization step copies the latest POS inventory back to the website so online shoppers see current availability.',
  },
  {
    id: 7,
    title: 'Low Stock',
    caption: 'The system detects a product approaching its reorder threshold.',
    narration:
      'When stock falls near the minimum threshold, the demo flags the product so the owner can review it.',
  },
  {
    id: 8,
    title: 'Reorder Recommendation',
    caption: 'Current 8 · Minimum 10 · Velocity 4/day · Suggested 30',
    narration:
      'For example, Product X shows eight units on hand, a minimum of ten, average daily sales of four, and a suggested reorder of thirty. Actual calculations would follow the store’s business rules and supplier data.',
  },
  {
    id: 9,
    title: 'Owner Benefit',
    caption: 'One connected view of sales, stock, online orders, and reorders.',
    narration:
      'The owner sees what is selling, what is running low, what customers are ordering online, what needs reordering, and how inventory is moving across online and in-store sales. One connected system can give the owner a clearer picture of inventory and sales.',
  },
] as const;

export const FULL_NARRATION_SCRIPT = `
HOW POS & INVENTORY INTEGRATION COULD WORK
Duration target: about 90 seconds. Demo concept only — not a live POS recording.

Scene 1 — Customer Orders
${SCENES[0].narration}

Scene 2 — Order Reaches Store
${SCENES[1].narration}

Scene 3 — POS
${SCENES[2].narration}

Scene 4 — Inventory
${SCENES[3].narration}

Scene 5 — In-Store Sale
${SCENES[4].narration}

Scene 6 — Website Updates
${SCENES[5].narration}

Scene 7 — Low Stock
${SCENES[6].narration}

Scene 8 — Reorder Recommendation
${SCENES[7].narration}

Scene 9 — Owner Benefit
${SCENES[8].narration}

End card: This demonstration uses simulated data. Connecting a real store requires identifying the POS and inventory software first.
`.trim();
