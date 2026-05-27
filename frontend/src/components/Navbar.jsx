import { useEffect, useMemo, useState } from 'react';
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../api/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [compact, setCompact] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setCompact(window.scrollY > 20);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => {
    setDropdownOpen(false);
  }, [location.pathname]);

  const initials = useMemo(() => {
    const value = (user?.username || user?.email || 'ER').trim();
    if (!value) return 'ER';
    const parts = value.split(/\s+/).filter(Boolean);
    if (parts.length > 1) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    return value.slice(0, 2).toUpperCase();
  }, [user]);

  const handleLogout = async () => {
    setDropdownOpen(false);
    await logout();
    navigate('/login');
  };

  const navItems = [
    { to: '/home', label: 'Home' },
    { to: '/dietplanner', label: 'Plan My Diet' },
    { to: '/bodymass', label: 'Body Fat' },
    { to: '/chatbot', label: 'AI Chatbot' },
  ];
  if (user) {
    navItems.push({ to: '/progress', label: 'Progress' });
    navItems.push({ to: '/diet-history', label: 'History' });
  }

  return (
    <motion.header
      className="site-header"
      animate={{}}
      transition={{ duration: 0.2 }}
    >
      <motion.div className="site-header__inner" animate={{ height: compact ? 56 : 72 }} transition={{ duration: 0.22 }}>
        {/* Logo - Far Left */}
        <Link to="/home" aria-label="EatRight home" className="header-logo-wrapper">
          <img className="site-logo site-logo--nav" src="/static/images/logo.png" alt="EatRight" />
        </Link>

        {/* Navigation - Center */}
        <nav className="site-header__nav" aria-label="Main navigation">
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}>
              {({ isActive }) => (
                <>
                  {item.label}
                  {isActive && <span className="nav-dot" />}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Account Badge - Far Right */}
        <div className="header-account-wrapper">
          {user ? (
            <button className="avatar-btn" onClick={() => setDropdownOpen(open => !open)} aria-label="Profile menu">
              {initials}
            </button>
          ) : (
            <Link to="/login" className="login-cta">Login</Link>
          )}

          {user && dropdownOpen && (
            <div className="nav-dropdown">
              <Link to="/profile">Profile</Link>
              <button onClick={handleLogout}>Logout</button>
            </div>
          )}
        </div>
      </motion.div>
    </motion.header>
  );
}
