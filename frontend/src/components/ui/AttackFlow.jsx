import { useEffect, useRef } from 'react'

const SCENARIOS = [
  { label: 'Goal\nDeviation', icon: '🎯' },
  { label: 'Excessive\nAgency', icon: '⚡' },
  { label: 'Indirect\nInjection', icon: '🪤' },
  { label: 'Permission\nBoundary', icon: '🔒' },
  { label: 'Multi-step\nChain', icon: '🔗' },
  { label: 'Role-play\nJailbreak', icon: '🎭' },
  { label: 'Token\nSmuggling', icon: '📦' },
  { label: 'Context\nWindow\nOverflow', icon: '🌊' },
  { label: 'Tool\nAbuse', icon: '🔧' },
]

export default function AttackFlow({ cycle = 0, completed = 0 }) {
  const ref = useRef(null)
  const ready = useRef(false)

  useEffect(() => {
    const canvas = ref.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const n = SCENARIOS.length
    const baseH = 160

    function getWidth() {
      return canvas.offsetWidth || canvas.parentElement?.offsetWidth || 0
    }

    function doDraw() {
      const w = getWidth()
      if (w < 1) return

      canvas.width = w * 2
      canvas.height = baseH * 2
      ctx.setTransform(2, 0, 0, 2, 0, 0)

      const spacing = Math.min(110, (w - 60) / (n - 1))
      const startX = (w - spacing * (n - 1)) / 2
      const cy = baseH / 2

      ctx.clearRect(0, 0, w, baseH)

      for (let i = 0; i < n - 1; i++) {
        const x1 = startX + i * spacing + 18
        const x2 = startX + (i + 1) * spacing - 18
        const passed = completed > i
        ctx.beginPath()
        ctx.moveTo(x1, cy)
        ctx.lineTo(x2, cy)
        ctx.strokeStyle = passed ? 'rgba(6,182,212,0.4)' : 'rgba(255,255,255,0.08)'
        ctx.lineWidth = passed ? 2 : 1
        ctx.stroke()

        if (i === completed && completed < n) {
          const progress = (cycle % 60) / 60
          const dotX = x1 + (x2 - x1) * progress
          ctx.beginPath()
          ctx.arc(dotX, cy, 4, 0, Math.PI * 2)
          ctx.fillStyle = '#06B6D4'
          ctx.shadowColor = '#06B6D4'
          ctx.shadowBlur = 12
          ctx.fill()
          ctx.shadowBlur = 0
        }
      }

      SCENARIOS.forEach((s, i) => {
        const x = startX + i * spacing
        const pass = completed > i
        const active = completed === i
        const color = pass ? '#06B6D4' : active ? '#F59E0B' : 'rgba(255,255,255,0.15)'
        const r = active ? 22 : 18

        ctx.beginPath()
        ctx.arc(x, cy, r, 0, Math.PI * 2)
        ctx.fillStyle = pass ? 'rgba(6,182,212,0.1)' : active ? 'rgba(245,158,11,0.08)' : 'rgba(255,255,255,0.03)'
        ctx.fill()
        ctx.strokeStyle = color
        ctx.lineWidth = active ? 2.5 : 1.5
        ctx.shadowColor = active ? '#06B6D4' : 'transparent'
        ctx.shadowBlur = active ? 15 : 0
        ctx.stroke()
        ctx.shadowBlur = 0

        ctx.font = '14px sans-serif'
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.fillStyle = color
        ctx.fillText(s.icon, x, cy)
      })
    }

    doDraw()

    const ro = new ResizeObserver(() => {
      const parent = canvas.parentElement
      if (parent && parent.offsetWidth > 0) {
        doDraw()
        ro.disconnect()
      }
    })
    ro.observe(canvas.parentElement || canvas)
    return () => ro.disconnect()
  }, [cycle, completed])

  return (
    <canvas
      ref={ref}
      className="w-full rounded-xl bg-black/30 border border-white/5"
      style={{ height: 160, boxShadow: '0 0 20px rgba(6,182,212,0.03)' }}
    />
  )
}
