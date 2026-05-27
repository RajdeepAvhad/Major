import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { CheckCircle2, Eye, EyeOff, Lock, Mail, User } from 'lucide-react';
import { useAuth } from '../api/AuthContext';
import GlassCard from '../components/GlassCard';

export default function LoginPage() {
  const { login, signup } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode]     = useState('login'); // 'login' | 'signup'
  const [error, setError]   = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassLogin, setShowPassLogin] = useState(false);
  const [showPassSignup, setShowPassSignup] = useState(false);
  const [showPassSignup2, setShowPassSignup2] = useState(false);
  const [successTick, setSuccessTick] = useState(false);
  const [shake, setShake] = useState(false);

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
    if (res.ok) {
      setSuccessTick(true);
      setTimeout(() => navigate('/home'), 650);
      return;
    }
    setLoading(false);
    setError(res.message || 'Login failed');
    setShake(true);
    setTimeout(() => setShake(false), 350);
  };

  const handleSignup = async e => {
    e.preventDefault();
    setError(''); setLoading(true);
    const res = await signup(sUser, sEmail, sPass, sPass2);
    if (res.ok) {
      setSuccessTick(true);
      setTimeout(() => navigate('/home'), 650);
      return;
    }
    setLoading(false);
    setError(res.message || 'Signup failed');
    setShake(true);
    setTimeout(() => setShake(false), 350);
  };

  return (
    <div className="login-container" style={{ position: 'relative' }}>
      <div className="login-aurora"><div /><div /></div>

      <GlassCard className={`login-box glassy ${shake ? 'shake' : ''}`} style={{ width: '100%', maxWidth: 460, padding: 30 }}>
        <div className="text-center mb-3">
          <img src="/static/images/logo.png" alt="EatRight" height="56" style={{ display: 'block', margin: '0 auto', filter: 'drop-shadow(0 0 12px rgba(34,197,94,0.3))' }} />
        </div>
        <h2 style={{ textAlign: 'center' }}>EatRight</h2>

        <div className="login-tab-shell mb-3">
          <div className={`login-tab-slider ${mode === 'signup' ? 'signup' : ''}`} />
          <button className="login-tab" onClick={() => { setMode('login'); setError(''); }}>Login</button>
          <button className="login-tab" onClick={() => { setMode('signup'); setError(''); }}>Sign Up</button>
        </div>

        {error && <div className="alert alert-danger py-2" style={{ background: '#3d3d3d', color: '#27AE60', border: '1px solid #27AE60' }}>{error}</div>}

        {mode === 'login' ? (
          <form onSubmit={handleLogin}>
            <div className={`floating-field ${lUser ? 'has-value' : ''}`}>
              <User size={16} className="field-icon" />
              <input value={lUser} onChange={e => setLUser(e.target.value)} required placeholder=" " />
              <label>Username</label>
            </div>

            <div className={`floating-field ${lPass ? 'has-value' : ''}`} style={{ marginTop: 12 }}>
              <Lock size={16} className="field-icon" />
              <input type={showPassLogin ? 'text' : 'password'} value={lPass} onChange={e => setLPass(e.target.value)} required placeholder=" " style={{ paddingRight: 40 }} />
              <label>Password</label>
              <button type="button" onClick={() => setShowPassLogin(v => !v)} style={{ position: 'absolute', right: 10, top: 12, background: 'transparent', border: 'none', color: '#9ca3af' }}>
                {showPassLogin ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>

            <button className="btn-green shimmer-btn w-100" style={{ marginTop: 16 }} type="submit" disabled={loading || successTick}>
              {successTick ? <span style={{ display: 'inline-flex', gap: 8, alignItems: 'center' }}><CheckCircle2 size={18} /> Success</span> : (loading ? 'Logging in...' : 'Login')}
            </button>
          </form>
        ) : (
          <form onSubmit={handleSignup}>
            <div className={`floating-field ${sUser ? 'has-value' : ''}`}>
              <User size={16} className="field-icon" />
              <input value={sUser} onChange={e => setSUser(e.target.value)} required placeholder=" " />
              <label>Username</label>
            </div>

            <div className={`floating-field ${sEmail ? 'has-value' : ''}`} style={{ marginTop: 12 }}>
              <Mail size={16} className="field-icon" />
              <input type="email" value={sEmail} onChange={e => setSEmail(e.target.value)} required placeholder=" " />
              <label>Email</label>
            </div>

            <div className={`floating-field ${sPass ? 'has-value' : ''}`} style={{ marginTop: 12 }}>
              <Lock size={16} className="field-icon" />
              <input type={showPassSignup ? 'text' : 'password'} value={sPass} onChange={e => setSPass(e.target.value)} required placeholder=" " style={{ paddingRight: 40 }} />
              <label>Password</label>
              <button type="button" onClick={() => setShowPassSignup(v => !v)} style={{ position: 'absolute', right: 10, top: 12, background: 'transparent', border: 'none', color: '#9ca3af' }}>
                {showPassSignup ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>

            <div className={`floating-field ${sPass2 ? 'has-value' : ''}`} style={{ marginTop: 12 }}>
              <Lock size={16} className="field-icon" />
              <input type={showPassSignup2 ? 'text' : 'password'} value={sPass2} onChange={e => setSPass2(e.target.value)} required placeholder=" " style={{ paddingRight: 40 }} />
              <label>Confirm Password</label>
              <button type="button" onClick={() => setShowPassSignup2(v => !v)} style={{ position: 'absolute', right: 10, top: 12, background: 'transparent', border: 'none', color: '#9ca3af' }}>
                {showPassSignup2 ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>

            <button className="btn-green shimmer-btn w-100" style={{ marginTop: 16 }} type="submit" disabled={loading || successTick}>
              {successTick ? <span style={{ display: 'inline-flex', gap: 8, alignItems: 'center' }}><CheckCircle2 size={18} /> Success</span> : (loading ? 'Creating account...' : 'Sign Up')}
            </button>
          </form>
        )}

        <AnimatePresence>
          {successTick && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={{ marginTop: 12, color: '#86efac', textAlign: 'center' }}>
              Redirecting...
            </motion.div>
          )}
        </AnimatePresence>
      </GlassCard>
    </div>
  );
}
