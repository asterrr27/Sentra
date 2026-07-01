import { useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'

function ParticleField() {
  const ref = useRef(null)

  useEffect(() => {
    const canvas = ref.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    let animId

    function resize() {
      canvas.width = canvas.offsetWidth * 2
      canvas.height = canvas.offsetHeight * 2
    }
    resize()
    window.addEventListener('resize', resize)

    const particles = Array.from({ length: 60 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.5,
      vy: (Math.random() - 0.5) * 0.5,
      r: Math.random() * 2 + 1,
    }))

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      particles.forEach((p, i) => {
        p.x += p.vx
        p.y += p.vy
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1

        ctx.beginPath()
        ctx.arc(p.x / 2, p.y / 2, p.r, 0, Math.PI * 2)
        ctx.fillStyle = 'rgba(6,182,212,0.4)'
        ctx.fill()

        for (let j = i + 1; j < particles.length; j++) {
          const dx = (particles[j].x - p.x) / 2
          const dy = (particles[j].y - p.y) / 2
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < 150) {
            ctx.beginPath()
            ctx.moveTo(p.x / 2, p.y / 2)
            ctx.lineTo(particles[j].x / 2, particles[j].y / 2)
            ctx.strokeStyle = `rgba(6,182,212,${0.1 * (1 - dist / 150)})`
            ctx.lineWidth = 0.5
            ctx.stroke()
          }
        }
      })
      animId = requestAnimationFrame(draw)
    }
    draw()
    return () => { cancelAnimationFrame(animId); window.removeEventListener('resize', resize) }
  }, [])

  return <canvas ref={ref} className="absolute inset-0 w-full h-full pointer-events-none" style={{ opacity: 0.6 }} />
}

export default function Hero() {
  return (
    <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden cyber-grid">
      <ParticleField />

      {/* Gradient orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-[120px] animate-pulse-glow" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-secondary/10 rounded-full blur-[100px] animate-pulse-glow" style={{ animationDelay: '1.5s' }} />

      <div className="relative z-10 max-w-4xl mx-auto px-4 text-center pt-24 pb-16">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
        >
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/5 border border-primary/20 text-primary text-xs font-medium mb-6">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            AI Agent Security Platform
          </div>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1, ease: 'easeOut' }}
          className="text-4xl sm:text-5xl md:text-7xl font-black tracking-tight leading-[1.1] mb-6"
        >
          Stress Test Your{' '}
          <span className="gradient-text">AI Agent</span>
          <br />
          Before Attackers Do.
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2, ease: 'easeOut' }}
          className="text-lg sm:text-xl text-white/50 max-w-2xl mx-auto mb-10 leading-relaxed"
        >
          Paste your deployed AI Agent URL and let Sentra simulate real-world attacks
          to discover vulnerabilities before attackers do.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3, ease: 'easeOut' }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <Link
            to="/dashboard"
            className="px-8 py-3.5 text-base font-semibold text-[#09090B] bg-gradient-to-r from-primary to-secondary rounded-full hover:shadow-xl hover:shadow-primary/20 transition-all"
          >
            Start Free Audit
          </Link>
          <Link
            to="/demo"
            className="px-8 py-3.5 text-base font-medium text-white/70 border border-white/20 rounded-full hover:border-primary/50 hover:text-primary transition-all"
          >
            View Demo Report
          </Link>
        </motion.div>

        {/* How it works flow */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl mx-auto"
        >
          {[
            { icon: '🤖', label: 'AI Agent', desc: 'Paste your URL' },
            { icon: '⚙️', label: 'Security Engine', desc: 'Analysis begins' },
            { icon: '⚡', label: 'Attack Simulation', desc: '5 attack types' },
            { icon: '📋', label: 'Security Report', desc: 'Actionable insights' },
          ].map((step, i) => (
            <div key={step.label} className="relative">
              <div className="glass-card p-4 text-center hover:border-primary/20 transition-colors">
                <div className="text-2xl mb-2">{step.icon}</div>
                <div className="text-sm font-semibold text-white">{step.label}</div>
                <div className="text-[10px] text-white/40 mt-0.5">{step.desc}</div>
              </div>
              {i < 3 && (
                <div className="hidden md:block absolute top-1/2 -right-3 text-primary/30 text-lg">→</div>
              )}
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
