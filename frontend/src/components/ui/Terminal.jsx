import { useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export default function Terminal({ lines = [] }) {
  const ref = useRef(null)

  useEffect(() => {
    if (ref.current) ref.current.scrollTop = ref.current.scrollHeight
  }, [lines])

  return (
    <div
      ref={ref}
      className="bg-black/60 border border-primary/20 rounded-xl p-4 font-mono text-xs leading-relaxed h-40 overflow-y-auto"
      style={{ boxShadow: 'inset 0 0 30px rgba(0,0,0,0.4), 0 0 20px rgba(6,182,212,0.04)' }}
    >
      <AnimatePresence>
        {lines.map((line, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.2, delay: i === lines.length - 1 ? 0 : 0 }}
            className={`${line.type === 'pass' ? 'text-success' : line.type === 'fail' ? 'text-danger' : line.type === 'info' ? 'text-white/40' : 'text-primary'} ${line.type !== 'info' ? 'before:content-["$\\00a0"] before:text-primary/50' : ''}`}
          >
            {line.type === 'pass' && '✅ '}
            {line.type === 'fail' && '❌ '}
            {line.text}
          </motion.div>
        ))}
      </AnimatePresence>
      <motion.span
        animate={{ opacity: [1, 0] }}
        transition={{ duration: 0.8, repeat: Infinity }}
        className="text-primary"
      >█</motion.span>
    </div>
  )
}
