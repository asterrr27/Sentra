import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import Hero from '../components/landing/Hero'
import TrustSection from '../components/landing/TrustSection'
import FeaturesSection from '../components/landing/FeaturesSection'
import PlatformSection from '../components/landing/PlatformSection'
import PageTransition from '../components/layout/PageTransition'

export default function Landing() {
  return (
    <PageTransition>
      <Hero />
      <TrustSection />
      <FeaturesSection />
      <PlatformSection />

      {/* CTA */}
      <section className="py-20">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="glass-card p-10 sm:p-14 border-primary/10 neon-glow"
          >
            <h2 className="text-2xl sm:text-3xl font-bold mb-4">Ready to Secure Your AI Agent?</h2>
            <p className="text-white/40 mb-8 max-w-md mx-auto">
              Start with a free audit. No credit card required. No setup needed.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
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
                Watch Demo
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer for landing */}
      <footer className="border-t border-white/5 py-8">
        <div className="max-w-6xl mx-auto px-4 text-center text-xs text-white/20">
          &copy; {new Date().getFullYear()} Sentra. Secure AI. Build with Confidence.
        </div>
      </footer>
    </PageTransition>
  )
}
