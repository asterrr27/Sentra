import { expect, afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'

afterEach(() => {
  cleanup()
})

globalThis.IntersectionObserver = class IntersectionObserver {
  constructor() { this.observe = () => {}; this.unobserve = () => {}; this.disconnect = () => {} }
  observe() {}
  unobserve() {}
  disconnect() {}
}

globalThis.HTMLCanvasElement.prototype.getContext = () => ({
  clearRect: () => {},
  fillRect: () => {},
  fillText: () => {},
  beginPath: () => {},
  arc: () => {},
  fill: () => {},
  stroke: () => {},
  moveTo: () => {},
  lineTo: () => {},
  createRadialGradient: () => ({ addColorStop: () => {} }),
})
