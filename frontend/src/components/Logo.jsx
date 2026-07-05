import { motion } from 'framer-motion'
import { useId } from 'react'

export default function Logo({ size = 32, withText = false, className = '' }) {
  const gradientId = useId()
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <svg width={size} height={size} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#06B6D4" />
            <stop offset="100%" stopColor="#8B5CF6" />
          </linearGradient>
        </defs>
        <rect width="32" height="32" rx="8" fill="#09090B" stroke="url(#logo-gradient)" strokeWidth="1.5" />
        <motion.path
          d="M 16 5 L 27 10 L 27 19 L 16 26 L 5 19 L 5 10 Z"
          stroke={`url(#${gradientId})`}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1.5, ease: 'easeInOut' }}
        />
        <motion.circle
          cx="16" cy="15" r="2"
          fill="#06B6D4"
          style={{ transformOrigin: '16px 15px' }}
          animate={{ scale: [0.8, 1.2, 0.8], opacity: [0.4, 1, 0.4] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      </svg>
      {withText && (
        <span className="text-lg font-bold tracking-tight">
          <span className="gradient-text">Sentra</span>
        </span>
      )}
    </div>
  )
}
