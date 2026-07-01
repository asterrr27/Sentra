import { Link } from 'react-router-dom'
import Logo from '../Logo'

const FOOTER_LINKS = {
  Product: [
    { label: 'Dashboard', to: '/dashboard' },
    { label: 'Payloads', to: '/payloads' },
    { label: 'Demo', to: '/demo' },
  ],
  Company: [
    { label: 'About', href: '#' },
    { label: 'Blog', href: '#' },
    { label: 'GitHub', href: '#' },
  ],
  Legal: [
    { label: 'Privacy Policy', href: '#' },
    { label: 'Terms of Service', href: '#' },
  ],
}

export default function Footer() {
  return (
    <footer className="border-t border-white/5 bg-[#09090B]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div className="col-span-2 md:col-span-1">
            <Link to="/" className="flex items-center gap-2 mb-4">
              <Logo size={24} />
              <span className="font-bold gradient-text">Sentra</span>
            </Link>
            <p className="text-sm text-white/40 max-w-xs leading-relaxed">
              Modern AI Agent Security Platform. Secure AI. Build with Confidence.
            </p>
          </div>
          {Object.entries(FOOTER_LINKS).map(([title, links]) => (
            <div key={title}>
              <h4 className="text-xs font-semibold text-white/30 uppercase tracking-widest mb-4">{title}</h4>
              <ul className="space-y-2">
                {links.map(link => (
                  <li key={link.label}>
                    {link.to ? (
                      <Link to={link.to} className="text-sm text-white/50 hover:text-primary transition-colors">
                        {link.label}
                      </Link>
                    ) : (
                      <a href={link.href} className="text-sm text-white/50 hover:text-primary transition-colors">
                        {link.label}
                      </a>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="mt-12 pt-8 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-white/30">
            &copy; {new Date().getFullYear()} Sentra. All rights reserved.
          </p>
          <div className="flex items-center gap-4">
            {['GitHub', 'Twitter', 'Discord'].map(social => (
              <a key={social} href="#" className="text-xs text-white/30 hover:text-primary transition-colors">
                {social}
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  )
}
