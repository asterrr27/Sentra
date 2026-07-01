import { motion } from 'framer-motion'

const PLATFORMS = [
  { name: 'OpenAI Agents', icon: '🤖' },
  { name: 'LangChain', icon: '⛓️' },
  { name: 'CrewAI', icon: '👥' },
  { name: 'AutoGen', icon: '🔄' },
  { name: 'MCP', icon: '🔌' },
  { name: 'REST APIs', icon: '🌐' },
  { name: 'Custom AI Agents', icon: '⚙️' },
]

export default function PlatformSection() {
  return (
    <section className="py-20 border-y border-white/5">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold mb-3">Works With Any AI Agent</h2>
          <p className="text-white/40 max-w-lg mx-auto">Support for all major AI agent frameworks and custom deployments</p>
        </div>
        <div className="flex flex-wrap justify-center gap-3">
          {PLATFORMS.map((p, i) => (
            <motion.div
              key={p.name}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.3, delay: i * 0.05 }}
              className="glass-card px-5 py-3 flex items-center gap-2 hover:border-primary/20 transition-colors"
            >
              <span className="text-lg">{p.icon}</span>
              <span className="text-sm font-medium text-white/70">{p.name}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
