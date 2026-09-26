import { useEffect, useMemo, useState } from 'react';
import { PRODUCTS } from '../lib/products';
import { CATEGORIES } from '../lib/store-info';
import { loadState } from '../lib/demo-store';
import { formatMoney, stockStatus, statusLabel } from '../lib/inventory-math';
import type { CategoryId, StockStatus } from '../lib/types';
import ProductArt from './ProductArt';

interface Props {
  initialCategory?: string;
}

type SortKey = 'featured' | 'price-asc' | 'price-desc' | 'name';

export default function ShopCatalog({ initialCategory = '' }: Props) {
  const [q, setQ] = useState('');
  const [category, setCategory] = useState(initialCategory);
  const [maxPrice, setMaxPrice] = useState(100);
  const [availability, setAvailability] = useState<'all' | 'in_stock' | 'low'>('all');
  const [sort, setSort] = useState<SortKey>('featured');
  const [qtyMap, setQtyMap] = useState<Record<string, number>>({});

  useEffect(() => {
    const state = loadState();
    const map: Record<string, number> = {};
    for (const r of state.websiteInventory) map[r.productId] = r.quantity;
    setQtyMap(map);
  }, []);

  const filtered = useMemo(() => {
    let list = [...PRODUCTS];
    if (category) list = list.filter((p) => p.category === category);
    if (q.trim()) {
      const needle = q.trim().toLowerCase();
      list = list.filter(
        (p) =>
          p.name.toLowerCase().includes(needle) ||
          p.brand.toLowerCase().includes(needle) ||
          p.sku.toLowerCase().includes(needle),
      );
    }
    list = list.filter((p) => p.price <= maxPrice);
    list = list.filter((p) => {
      const qty = qtyMap[p.id] ?? 0;
      if (availability === 'in_stock') return qty > 0;
      if (availability === 'low') {
        const inv = loadState().websiteInventory.find((r) => r.productId === p.id);
        if (!inv) return false;
        const s: StockStatus = stockStatus(inv);
        return s === 'low' || s === 'reorder';
      }
      return true;
    });
    switch (sort) {
      case 'price-asc':
        list.sort((a, b) => a.price - b.price);
        break;
      case 'price-desc':
        list.sort((a, b) => b.price - a.price);
        break;
      case 'name':
        list.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'featured':
      default:
        list.sort((a, b) => Number(!!b.featured) - Number(!!a.featured) || a.name.localeCompare(b.name));
        break;
    }
    return list;
  }, [q, category, maxPrice, availability, sort, qtyMap]);

  return (
    <div>
      <div className="filters" role="search">
        <label>
          Search
          <input
            type="search"
            placeholder="Name, brand, or SKU"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </label>
        <label>
          Category
          <select value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="">All</option>
            {CATEGORIES.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Max price ${maxPrice}
          <input
            type="range"
            min={5}
            max={100}
            value={maxPrice}
            onChange={(e) => setMaxPrice(Number(e.target.value))}
          />
        </label>
        <label>
          Availability
          <select
            value={availability}
            onChange={(e) => setAvailability(e.target.value as typeof availability)}
          >
            <option value="all">All</option>
            <option value="in_stock">In stock</option>
            <option value="low">Low / reorder</option>
          </select>
        </label>
        <label>
          Sort
          <select value={sort} onChange={(e) => setSort(e.target.value as SortKey)}>
            <option value="featured">Featured</option>
            <option value="price-asc">Price: low to high</option>
            <option value="price-desc">Price: high to low</option>
            <option value="name">Name</option>
          </select>
        </label>
      </div>
      <p style={{ color: 'var(--muted)', marginBottom: '1rem' }}>
        Showing {filtered.length} demo products
        {category ? ` in ${CATEGORIES.find((c) => c.id === (category as CategoryId))?.name ?? category}` : ''}.
      </p>
      <div className="grid-3">
        {filtered.map((product) => {
          const qty = qtyMap[product.id] ?? 0;
          const inv = loadState().websiteInventory.find((r) => r.productId === product.id);
          const status = inv ? stockStatus(inv) : qty > 0 ? 'healthy' : 'out';
          return (
            <a key={product.id} className="card product-card" href={`/products/${product.slug}/`}>
              <div className="product-art" style={{ background: `hsl(${product.imageHue} 25% 92%)` }}>
                <ProductArt product={product} size={180} />
              </div>
              <div className="product-body">
                <span className="brand-label">{product.brand}</span>
                <h3>{product.name}</h3>
                <div className="price">{formatMoney(product.price)}</div>
                <span className={`badge ${status === 'healthy' ? 'badge-ok' : status === 'low' ? 'badge-warn' : 'badge-danger'}`}>
                  {statusLabel(status)} · {qty} left (demo)
                </span>
              </div>
            </a>
          );
        })}
      </div>
    </div>
  );
}
