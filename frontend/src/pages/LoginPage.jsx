import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../api/AuthContext';

export default function LoginPage() {
  const { login, signup } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode]     = useState('login'); // 'login' | 'signup'
  const [error, setError]   = useState('');
  const [loading, setLoading] = useState(false);

  // Login fields
  const [lUser, setLUser]   = useState('');
  const [lPass, setLPass]   = useState('');

  // Signup fields
  const [sUser, setSUser]   = useState('');
  const [sEmail, setSEmail] = useState('');
  const [sPass, setSPass]   = useState('');
  const [sPass2, setSPass2] = useState('');

  const handleLogin = async e => {
    e.preventDefault();
    setError(''); setLoading(true);
    const res = await login(lUser, lPass);
    setLoading(false);
    if (res.ok) navigate('/home');
    else setError(res.message || 'Login failed');
  };

  const handleSignup = async e => {
    e.preventDefault();
    setError(''); setLoading(true);
    const res = await signup(sUser, sEmail, sPass, sPass2);
    setLoading(false);
    if (res.ok) navigate('/home');
    else setError(res.message || 'Signup failed');
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="text-center mb-3">
          <img src="/static/images/Gemini_Generated_Image_f0bd5kf0bd5kf0bd.png" alt="EatRight" height="60" />
        </div>
        <h2>EatRight</h2>

        {/* Tabs */}
        <div className="login-tabs">
          <button className={`login-tab${mode === 'login' ? ' active' : ''}`} onClick={() => { setMode('login'); setError(''); }}>
            Login
          </button>
          <button className={`login-tab${mode === 'signup' ? ' active' : ''}`} onClick={() => { setMode('signup'); setError(''); }}>
            Sign Up
          </button>
        </div>

        {error && <div className="alert alert-danger py-2" style={{ background: '#3d3d3d', color: '#27AE60', border: '1px solid #27AE60' }}>{error}</div>}

        {mode === 'login' ? (
          <form onSubmit={handleLogin}>
            <div className="mb-3">
              <label className="form-label" style={{ color: '#e8e8e8' }}>Username</label>
              <input className="form-control" value={lUser} onChange={e => setLUser(e.target.value)} required placeholder="Enter username"
                style={{ background: '#3d3d3d', color: '#e8e8e8', border: '1px solid #555' }} />
            </div>
            <div className="mb-3">
              <label className="form-label" style={{ color: '#e8e8e8' }}>Password</label>
              <input className="form-control" type="password" value={lPass} onChange={e => setLPass(e.target.value)} required placeholder="Enter password"
                style={{ background: '#3d3d3d', color: '#e8e8e8', border: '1px solid #555' }} />
            </div>
            <button className="btn-brand w-100" type="submit" disabled={loading}>
              {loading ? 'Logging in…' : 'Login'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleSignup}>
            <div className="mb-3">
              <label className="form-label" style={{ color: '#e8e8e8' }}>Username</label>
              <input className="form-control" value={sUser} onChange={e => setSUser(e.target.value)} required placeholder="Choose a username"
                style={{ background: '#3d3d3d', color: '#e8e8e8', border: '1px solid #555' }} />
            </div>
            <div className="mb-3">
              <label className="form-label" style={{ color: '#e8e8e8' }}>Email</label>
              <input className="form-control" type="email" value={sEmail} onChange={e => setSEmail(e.target.value)} required placeholder="Enter email"
                style={{ background: '#3d3d3d', color: '#e8e8e8', border: '1px solid #555' }} />
            </div>
            <div className="mb-3">
              <label className="form-label" style={{ color: '#e8e8e8' }}>Password</label>
              <input className="form-control" type="password" value={sPass} onChange={e => setSPass(e.target.value)} required placeholder="Min 6 characters"
                style={{ background: '#3d3d3d', color: '#e8e8e8', border: '1px solid #555' }} />
            </div>
            <div className="mb-3">
              <label className="form-label" style={{ color: '#e8e8e8' }}>Confirm Password</label>
              <input className="form-control" type="password" value={sPass2} onChange={e => setSPass2(e.target.value)} required placeholder="Repeat password"
                style={{ background: '#3d3d3d', color: '#e8e8e8', border: '1px solid #555' }} />
            </div>
            <button className="btn-brand w-100" type="submit" disabled={loading}>
              {loading ? 'Creating account…' : 'Sign Up'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
