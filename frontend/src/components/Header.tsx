import { useState } from 'react'
import { NavLink, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import AuthModal from './AuthModal'
import { Layout, Search, FolderHeart, LogIn, LogOut, Sparkles } from 'lucide-react'

export default function Header() {
  const { token, clearAuth } = useAuth()
  const [showAuth, setShowAuth] = useState(false)

  return (
    <>
      <header className="sticky top-0 z-40 w-full bg-white/80 backdrop-blur-md border-b border-rs-border/50">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-10 h-10 bg-rs-dark rounded-xl flex items-center justify-center text-white shadow-lg group-hover:scale-105 transition-transform">
              <Sparkles size={22} />
            </div>
            <span className="text-xl font-bold tracking-tight text-rs-dark font-serif">RoomStyle AI</span>
          </Link>

          <nav className="hidden md:flex items-center gap-2 bg-stone-100/50 p-1.5 rounded-full border border-stone-200/50">
            <NavLink 
              to="/" 
              className={({ isActive }) => `nav-link ${isActive ? 'nav-link-active' : 'nav-link-inactive'}`}
            >
              <div className="flex items-center gap-2">
                <Layout size={16} />
                <span>Design</span>
              </div>
            </NavLink>
            <NavLink 
              to="/browse" 
              className={({ isActive }) => `nav-link ${isActive ? 'nav-link-active' : 'nav-link-inactive'}`}
            >
              <div className="flex items-center gap-2">
                <Search size={16} />
                <span>Browse</span>
              </div>
            </NavLink>
            <NavLink 
              to="/projects" 
              className={({ isActive }) => `nav-link ${isActive ? 'nav-link-active' : 'nav-link-inactive'}`}
            >
              <div className="flex items-center gap-2">
                <FolderHeart size={16} />
                <span>My Projects</span>
              </div>
            </NavLink>
          </nav>

          <div className="flex items-center gap-4">
            {token ? (
              <button 
                onClick={clearAuth}
                className="btn-secondary !py-2 !px-4 text-sm"
              >
                <LogOut size={16} />
                <span>Sign Out</span>
              </button>
            ) : (
              <button 
                onClick={() => setShowAuth(true)}
                className="btn-primary !py-2 !px-5 text-sm"
              >
                <LogIn size={16} />
                <span>Sign In</span>
              </button>
            )}
          </div>
        </div>
      </header>

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </>
  )
}
