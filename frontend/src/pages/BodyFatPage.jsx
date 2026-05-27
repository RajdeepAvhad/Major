import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, Calendar, Ruler, Scale, UserRound } from 'lucide-react';
import GlassCard from '../components/GlassCard';

export default function BodyFatPage() {
  const [height, setHeight] = useState('');
  const [weight, setWeight] = useState('');
  const [age, setAge]       = useState('');
  const [gender, setGender] = useState('m');
  const [result, setResult] = useState('');

  const calculate = () => {
    const h = parseFloat(height);
    const w = parseFloat(weight);
    const a = parseInt(age);
    if (!h || !w || !a) { setResult('Please fill all fields.'); return; }
    const bmi = w / (h * h);
    let bfp;
    if (gender === 'f') bfp = (1.20 * bmi) + (0.23 * a) - 5.4;
    else                bfp = (1.20 * bmi) + (0.23 * a) - 16.2;
    setResult(Number(bfp.toFixed(2)));
  };

  const bfValue = Number(result);
  const isValid = Number.isFinite(bfValue) && bfValue > 0;
  const percent = isValid ? Math.min(100, (bfValue / 40) * 100) : 0;
  const arc = 175.9;
  const color = isValid ? (bfValue < 18 ? '#22c55e' : bfValue < 26 ? '#f59e0b' : '#ef4444') : '#64748b';

  const getCategory = () => {
    if (!isValid) return 'Not available';
    if (bfValue < 18) return 'Healthy';
    if (bfValue < 26) return 'Borderline';
    return 'High';
  };

  const parseNumber = (v) => Number.parseFloat(v || 0);
  const bmiValue = (parseNumber(weight) && parseNumber(height)) ? (parseNumber(weight) / (parseNumber(height) * parseNumber(height))) : null;

  return (
    <motion.main className="bodymass-layout page-motion" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div className="hero-particles" aria-hidden="true">
        <span style={{ left: '12%', top: '80%', animationDelay: '0s', opacity: 0.04 }}>🥗</span>
        <span style={{ right: '14%', top: '84%', animationDelay: '1.1s', opacity: 0.04 }}>🥑</span>
      </div>

      <section className="bodymass-shell">
        <GlassCard className="p-4" style={{ width: '100%' }}>
          <h2 style={{ color: '#86efac', marginBottom: 16 }}>Body Fat % Calculator</h2>

          <div className={`floating-field ${height ? 'has-value' : ''}`}>
            <Ruler size={16} className="field-icon" />
            <input type="number" step="0.01" placeholder=" " value={height} onChange={e => setHeight(e.target.value)} />
            <label>Height (m)</label>
          </div>

          <div className={`floating-field ${weight ? 'has-value' : ''}`} style={{ marginTop: 12 }}>
            <Scale size={16} className="field-icon" />
            <input type="number" placeholder=" " value={weight} onChange={e => setWeight(e.target.value)} />
            <label>Weight (kg)</label>
          </div>

          <div className={`floating-field ${age ? 'has-value' : ''}`} style={{ marginTop: 12 }}>
            <Calendar size={16} className="field-icon" />
            <input type="number" placeholder=" " value={age} onChange={e => setAge(e.target.value)} />
            <label>Age</label>
          </div>

          <div style={{ marginTop: 14 }}>
            <label style={{ color: '#d1d5db' }}>Gender</label>
            <div className="toggle-pill" style={{ marginTop: 8 }}>
              <div className={`toggle-pill__slider ${gender === 'f' ? 'female' : ''}`} />
              <button type="button" onClick={() => setGender('m')}><UserRound size={14} style={{ marginRight: 4 }} /> Male</button>
              <button type="button" onClick={() => setGender('f')}><UserRound size={14} style={{ marginRight: 4 }} /> Female</button>
            </div>
          </div>

          <div className="d-flex gap-2 flex-wrap" style={{ marginTop: 16 }}>
            <motion.button whileTap={{ scale: 0.97 }} className="btn-green" onClick={calculate}>Calculate</motion.button>
            <motion.button whileTap={{ scale: 0.97 }} className="btn-outline" style={{ borderColor: 'rgba(239,68,68,0.4)' }} onClick={() => {
              setHeight(''); setWeight(''); setAge(''); setGender('m'); setResult('');
            }}>Reset</motion.button>
            <motion.div whileTap={{ scale: 0.97 }}>
              <Link to="/dietplanner" className="btn-outline" style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 8, borderColor: 'rgba(34,197,94,0.5)' }}>
                Plan My Diet <ArrowRight size={15} />
              </Link>
            </motion.div>
          </div>

          <div style={{ marginTop: 16 }}>
            {isValid ? (
              <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
                <div style={{ width: 140, margin: '0 auto', position: 'relative' }}>
                  <svg viewBox="0 0 72 72" width="140" height="140" style={{ transform: 'rotate(-90deg)' }}>
                    <circle cx="36" cy="36" r="28" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="8" />
                    <circle cx="36" cy="36" r="28" fill="none" stroke={color} strokeWidth="8" strokeLinecap="round" strokeDasharray={arc} strokeDashoffset={arc - (percent / 100) * arc} />
                  </svg>
                  <div style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center' }}>
                    <div style={{ textAlign: 'center' }}>
                      <strong style={{ fontSize: 28 }}>{bfValue}%</strong>
                      <div style={{ color: '#9ca3af' }}>{getCategory()}</div>
                    </div>
                  </div>
                </div>
                <GlassCard className="p-3 mt-3">
                  <div style={{ display: 'grid', gap: 6 }}>
                    <span>BMI: <strong>{bmiValue ? bmiValue.toFixed(1) : '—'}</strong></span>
                    <span>Estimated Category: <strong>{getCategory()}</strong></span>
                    <small style={{ color: '#94a3b8' }}>Maintain consistency in nutrition and hydration for better body composition.</small>
                  </div>
                </GlassCard>
              </motion.div>
            ) : (
              <div>
                <p style={{ color: '#9ca3af', marginBottom: 10 }}>Your body fat % will appear here</p>
                <div className="placeholder-shimmer" />
              </div>
            )}
          </div>
        </GlassCard>

        <div>
          <GlassCard className="p-4" style={{ minHeight: 560, background: 'linear-gradient(180deg, rgba(15,17,23,0.85), rgba(15,17,23,0.55)), url(/static/images/fresh-veggies-bg.jpg) center/cover' }}>
            <h3 style={{ color: '#dcfce7' }}>Health Snapshot</h3>
            <p style={{ color: '#cbd5e1' }}>Use this calculator before generating a full diet plan to improve calorie target accuracy.</p>
          </GlassCard>
        </div>
      </section>
    </motion.main>
  );
}
