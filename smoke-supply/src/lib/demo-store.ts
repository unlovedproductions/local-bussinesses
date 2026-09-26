import { createInitialState, CART_KEY, STORAGE_KEY, DEMO_STATE_VERSION } from './seed';
import type { CartItem, DemoState } from './types';
import { DemoInventoryAdapter, DemoPosAdapter, IntegrationService } from './adapters/demo';

function canUseStorage(): boolean {
  return typeof window !== 'undefined' && typeof localStorage !== 'undefined';
}

export function loadState(): DemoState {
  if (!canUseStorage()) return createInitialState();
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      const initial = createInitialState();
      localStorage.setItem(STORAGE_KEY, JSON.stringify(initial));
      return initial;
    }
    const parsed = JSON.parse(raw) as DemoState;
    if (parsed.version !== DEMO_STATE_VERSION) {
      const initial = createInitialState();
      localStorage.setItem(STORAGE_KEY, JSON.stringify(initial));
      return initial;
    }
    return parsed;
  } catch {
    const initial = createInitialState();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(initial));
    return initial;
  }
}

export function saveState(state: DemoState): void {
  if (!canUseStorage()) return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  window.dispatchEvent(new CustomEvent('demo-state-changed'));
}

export function updateState(updater: (s: DemoState) => DemoState): DemoState {
  const next = updater(loadState());
  saveState(next);
  return next;
}

export function resetDemoState(): DemoState {
  const initial = createInitialState();
  saveState(initial);
  if (canUseStorage()) localStorage.removeItem(CART_KEY);
  return initial;
}

export function loadCart(): CartItem[] {
  if (!canUseStorage()) return [];
  try {
    const raw = localStorage.getItem(CART_KEY);
    return raw ? (JSON.parse(raw) as CartItem[]) : [];
  } catch {
    return [];
  }
}

export function saveCart(items: CartItem[]): void {
  if (!canUseStorage()) return;
  localStorage.setItem(CART_KEY, JSON.stringify(items));
  window.dispatchEvent(new CustomEvent('cart-changed'));
}

export function getIntegration(): IntegrationService {
  const pos = new DemoPosAdapter(loadState, updateState);
  const inventory = new DemoInventoryAdapter(loadState, updateState);
  return new IntegrationService(pos, inventory);
}

/** SSR-safe website quantity from seed (static pages). Client uses live state. */
export function getSeedWebsiteQty(productId: string): number {
  const state = createInitialState();
  return state.websiteInventory.find((r) => r.productId === productId)?.quantity ?? 0;
}
