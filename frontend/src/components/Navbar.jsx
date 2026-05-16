import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../api/AuthContext';
import { useState } from 'react';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = async () => {
    setMenuOpen(false);
    setDropdownOpen(false);
    await logout();
    navigate('/login');
  };

  const closeAll = () => { setMenuOpen(false); setDropdownOpen(false); };

  return (
    <header className="site-header">
      <Link to="/home" onClick={closeAll}>
        <img src="/static/images/Gemini_Generated_Image_f0bd5kf0bd5kf0bd.png" alt="EatRight" height="55" />
      </Link>

      {/* Hamburger button — visible only on mobile via CSS */}
      <button
        className="hamburger-btn"
        onClick={() => setMenuOpen(o => !o)}
        aria-label="Toggle navigation"
      >
        {menuOpen ? '✕' : '☰'}
      </button>

      <ul className={`nav-links${menuOpen ? ' nav-open' : ''}`}>
        <li><Link to="/home"        onClick={closeAll}>Home</Link></li>
        <li><Link to="/dietplanner" onClick={closeAll}>Plan My Diet</Link></li>
        <li><Link to="/bodymass"    onClick={closeAll}>Body Fat Calculator</Link></li>
        <li><Link to="/dashboard"   onClick={closeAll}>AI Chatbot</Link></li>
        {user && <li><Link to="/progress"   onClick={closeAll}>📊 Progress</Link></li>}
        {user && <li><Link to="/diet-history" onClick={closeAll}>History</Link></li>}

        {user ? (
          <li style={{ position: 'relative' }}>
            <button
              className="btn-brand"
              onClick={() => setDropdownOpen(o => !o)}
            >
              {user.username} ▾
            </button>
            {dropdownOpen && (
              <div className="nav-dropdown">
                <Link
                  to="/profile"
                  onClick={closeAll}
                  style={{ display: 'block', padding: '10px 16px', color: '#e8e8e8', textDecoration: 'none' }}
                >
                  My Profile
                </Link>
                <button
                  onClick={handleLogout}
                  style={{
                    display: 'block', width: '100%', padding: '10px 16px',
                    background: 'none', border: 'none', textAlign: 'left',
                    cursor: 'pointer', color: '#27AE60', fontWeight: 500,
                  }}
                >
                  Logout
                </button>
              </div>
            )}
          </li>
        ) : (
          <li><Link to="/login" className="btn-brand" onClick={closeAll}>Login</Link></li>
        )}
      </ul>
    </header>
  );
}
