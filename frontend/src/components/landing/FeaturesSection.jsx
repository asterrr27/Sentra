import { motion } from 'framer-motion'

const FEATURES = [
  {
    icon: '🔗',
    title: 'URL-Based Agent Testing',
    desc: 'Paste your deployed AI Agent endpoint. No SDK installation or code changes required — just a URL.',
  },
  {
    icon: '⚡',
    title: 'Automatic Attack Engine',
    desc: 'Run 13 types of AI security attacks spanning 6 OWASP LLM Top 10 categories including prompt injection, role-play jailbreak, and more.',
  },
  {
    icon: '📊',
    title: 'Security Intelligence',
    desc: 'Risk scoring with detailed insights. OWASP-aligned vulnerability classification and actionable recommendations.',
  },
  {
    icon: '📄',
    title: 'Professional Reports',
    desc: 'Generate detailed PDF and CSV reports with attack evidence and actionable mitigation steps.',
  },
]

export default function FeaturesSection() {
  return (
    <section className="py-20">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold mb-3">Everything You Need to Secure Your AI</h2>
          <p className="text-white/40 max-w-lg mx-auto">Comprehensive security testing designed for modern AI agents</p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          {FEATURES.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-80px' }}
              transition={{ duration: 0.5, delay: i * 0.1, ease: 'easeOut' }}
              className="glass-card p-6 group cursor-default"
            >
              <div className="text-3xl mb-4 group-hover:scale-110 transition-transform duration-300">{f.icon}</div>
              <h3 className="text-base font-semibold text-white mb-2">{f.title}</h3>
              <p className="text-sm text-white/40 leading-relaxed">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
