import type { Product } from '../lib/types';

interface Props {
  product: Product;
  size?: number;
}

/** Original pack-mark SVG — not a photo of a real product. */
export default function ProductArt({ product, size = 160 }: Props) {
  const hue = product.imageHue;
  const label = product.brand.slice(0, 10);
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 200 200"
      role="img"
      aria-label={`${product.name} demo product illustration`}
    >
      <defs>
        <linearGradient id={`g-${product.id}`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor={`hsl(${hue} 35% 28%)`} />
          <stop offset="100%" stopColor={`hsl(${(hue + 40) % 360} 40% 18%)`} />
        </linearGradient>
      </defs>
      <rect width="200" height="200" fill={`hsl(${hue} 25% 92%)`} />
      <rect x="40" y="28" width="120" height="144" rx="10" fill={`url(#g-${product.id})`} />
      <rect x="52" y="42" width="96" height="36" rx="4" fill="rgba(255,255,255,0.14)" />
      <text
        x="100"
        y="65"
        textAnchor="middle"
        fill="#f6f1e8"
        fontFamily="Georgia, serif"
        fontSize="14"
        fontWeight="700"
      >
        {label}
      </text>
      <text
        x="100"
        y="120"
        textAnchor="middle"
        fill="#f6f1e8"
        fontFamily="system-ui, sans-serif"
        fontSize="11"
        opacity="0.85"
      >
        DEMO
      </text>
      <text
        x="100"
        y="145"
        textAnchor="middle"
        fill="#f6f1e8"
        fontFamily="system-ui, sans-serif"
        fontSize="10"
        opacity="0.7"
      >
        {product.sku.slice(0, 12)}
      </text>
    </svg>
  );
}
