import { useEffect, useState, useRef } from 'react'
import { useInView } from 'framer-motion'

export default function StatCounter({ value, suffix = '', label = '', prefix = '' }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })
  const [count, setCount] = useState(0)

  useEffect(() => {
    if (!isInView) return
    let raf
    const duration = 2000
    const startTime = performance.now()
    function step(now) {
      const elapsed = now - startTime
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      setCount(Math.round((value) * eased))
      if (progress < 1) raf = requestAnimationFrame(step)
    }
    raf = requestAnimationFrame(step)
    return () => { if (raf) cancelAnimationFrame(raf) }
  }, [isInView, value])

  return (
    <div ref={ref} className="text-center">
      <div className="text-3xl sm:text-4xl font-black gradient-text">
        {prefix}{count}{suffix}
      </div>
      <p className="text-sm text-white/40 mt-1">{label}</p>
    </div>
  )
}
