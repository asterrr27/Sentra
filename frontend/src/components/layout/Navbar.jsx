import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import Logo from '../Logo'
import { useAuth } from '../../context/AuthContext'

const NAV_ITEMS = [
  { path: '/', label: 'Home' },
  { path: '/dashboard', label: 'Dashboard' },
  { path: '/payloads', label: 'Payloads' },
]

export default function Navbar() {
  const location = useLocation()
  const { user, logout } = useAuth()
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => { setMobileOpen(false) }, [location])

  return (
    <motion.nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? 'bg-[#09090B]/80 backdrop-blur-xl border-b border-white/5 shadow-lg shadow-black/20'
          : 'bg-transparent'
      }`}
      initial={{ y: -80 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2 group">
            <Logo size={28} />
            <span className="text-lg font-bold gradient-text">Sentra</span>
          </Link>

          <div className="hidden md:flex items-center gap-1">
            {NAV_ITEMS.map(item => {
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`relative px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                    isActive ? 'text-white' : 'text-white/50 hover:text-white hover:bg-white/5'
                  }`}
                >
                  {item.label}
                  {isActive && (
                    <motion.div
                      layoutId="nav-active"
                      className="absolute inset-0 bg-white/5 rounded-lg -z-10"
                      transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                    />
                  )}
                </Link>
              )
            })}
            <div className="ml-4 pl-4 border-l border-white/10 flex items-center gap-2">
              {user ? (
                <>
                  {user.role === 'admin' && (
                    <Link to="/admin" className="px-3 py-1.5 text-xs font-medium text-purple-400 border border-purple-400/30 rounded-full hover:bg-purple-400/10 transition-colors">
                      Admin
                    </Link>
                  )}
                  <span className="text-xs text-white/30">{user.username}</span>
                  <button
                    onClick={logout}
                    className="px-3 py-1.5 text-xs font-medium border border-white/10 rounded-full hover:border-red-400/30 hover:text-red-400 transition-all text-white/50"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link to="/login" className="px-4 py-2 text-sm font-medium text-white/50 hover:text-white transition-colors">
                    Sign In
                  </Link>
                  <Link to="/register" className="px-5 py-2 text-sm font-medium text-[#09090B] bg-gradient-to-r from-primary to-secondary rounded-full hover:shadow-lg hover:shadow-primary/20 transition-all">
                    Sign Up
                  </Link>
                </>
              )}
              <Link
                to="/demo"
                className="px-4 py-2 text-sm font-medium text-primary border border-primary/30 rounded-full hover:bg-primary/10 transition-colors"
              >
                Demo
              </Link>
            </div>
          </div>

          <button
            className="md:hidden p-2 text-white/50 hover:text-white"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              {mobileOpen ? (
                <path d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
      </div>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-[#09090B]/95 backdrop-blur-xl border-b border-white/5 overflow-hidden"
          >
            <div className="px-4 py-4 space-y-2">
              {NAV_ITEMS.map(item => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`block px-4 py-3 rounded-lg text-sm font-medium ${
                    location.pathname === item.path ? 'text-white bg-white/5' : 'text-white/50'
                  }`}
                >
                  {item.label}
                </Link>
              ))}
              {user ? (
                <>
                  <div className="px-4 py-2 text-xs text-white/30">{user.username}</div>
                  <button onClick={logout} className="block w-full text-left px-4 py-3 text-sm font-medium text-red-400">
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link to="/login" className="block px-4 py-3 text-sm font-medium text-white/50">Sign In</Link>
                  <Link to="/register" className="block px-4 py-3 text-sm font-medium text-center text-[#09090B] bg-gradient-to-r from-primary to-secondary rounded-full">
                    Sign Up
                  </Link>
                </>
              )}
              <Link to="/demo" className="block px-4 py-3 text-sm font-medium text-primary">Demo</Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  )
}
