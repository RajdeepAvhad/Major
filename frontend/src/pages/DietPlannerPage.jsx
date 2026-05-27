import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { Calendar, Clock3, Leaf, Ruler, Scale, UserRound } from 'lucide-react';
import { apiGet, apiPost } from '../api/client';
import GlassCard from '../components/GlassCard';

export default function DietPlannerPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');

  const [form, setForm] = useState({
    age: '', weight: '', height: '', bodyfat: '',
    goal: 'healthy', activity: 'Heavy', gender: '', category: 'none',
    planPeriod: 'daily',
    planDate: new Date().toISOString().slice(0, 10),
    reminderTime: '',
  });

  // Live client-side body fat preview
  const [bfPreview, setBfPreview] = useState('');

  useEffect(() => {
    apiGet('/api/preferences/')
      .then(res => {
        if (!res.ok || !res.preferences) return;
        const pref = res.preferences;
        const next = {
          ...form,
          age: pref.age ?? form.age,
          weight: pref.weight ?? form.weight,
          height: pref.height ?? form.height,
          bodyfat: pref.bodyfat ?? form.bodyfat,
          goal: pref.goal || form.goal,
          activity: pref.activity || form.activity,
          gender: pref.gender || form.gender,
          category: pref.category || form.category,
          planPeriod: pref.plan_period || form.planPeriod,
          planDate: pref.plan_date || form.planDate,
          reminderTime: pref.reminder_time || form.reminderTime,
        };
        setForm(next);
        const { weight: w, height: h, age: a, gender: g } = next;
        if (w && h && a && g && !next.bodyfat) {
          const hm = parseFloat(h) / 100;
          const bmi = parseFloat(w) / (hm * hm);
          const bf = g === 'female'
            ? (1.20 * bmi) + (0.23 * parseFloat(a)) - 5.4
            : (1.20 * bmi) + (0.23 * parseFloat(a)) - 16.2;
          setBfPreview(bf.toFixed(2));
        }
      })
      .catch(() => {});
  }, []);

  const set = (k, v) => {
    const updated = { ...form, [k]: v };
    setForm(updated);

    // recalculate preview
    const { weight: w, height: h, age: a, gender: g } = updated;
    if (w && h && a && g && !updated.bodyfat) {
      const hm = parseFloat(h) / 100;
      const bmi = parseFloat(w) / (hm * hm);
      const bf = g === 'female'
        ? (1.20 * bmi) + (0.23 * parseFloat(a)) - 5.4
        : (1.20 * bmi) + (0.23 * parseFloat(a)) - 16.2;
      setBfPreview(bf.toFixed(2));
    } else {
      setBfPreview('');
    }
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setError(''); setLoading(true);
    try {
      const res = await apiPost('/api/recommend/', {
        age: parseInt(form.age),
        weight: parseInt(form.weight),
        height: parseInt(form.height),
        bodyfat: form.bodyfat ? parseFloat(form.bodyfat) : null,
        goal: form.goal,
        activity: form.activity,
        gender: form.gender,
        category: form.category,
      });
      if (res.ok) {
        await apiPost('/api/preferences/save/', {
          age: parseInt(form.age),
          weight: parseInt(form.weight),
          height: parseInt(form.height),
          bodyfat: form.bodyfat ? parseFloat(form.bodyfat) : null,
          goal: form.goal,
          activity: form.activity,
          gender: form.gender,
          category: form.category,
          plan_period: form.planPeriod,
          plan_date: form.planDate,
          reminder_time: form.reminderTime,
        });
        // Store in sessionStorage so results survive refresh
        const payload = { ...res, plan_period: form.planPeriod, plan_date: form.planDate };
        sessionStorage.setItem('dietResults', JSON.stringify(payload));
        navigate('/diet-results');
      } else {
        setError(res.message || 'Something went wrong. Please try again.');
      }
    } catch {
      setError('Network error. Make sure Django server is running.');
    }
    setLoading(false);
  };

  return (
    <motion.main className="page-motion">
      <div className="form-shell">
        <motion.div className="form-hero" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <h1 style={{ marginBottom: 8 }}>Diet Planner</h1>
          <p style={{ color: '#cbd5e1', marginBottom: 12 }}>Step 1 of 2 — Your Details</p>
          <div className="progress-track"><span /></div>
        </motion.div>

        <GlassCard className="p-4 p-md-5">
          <h2 style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 18 }}><Leaf size={18} color="#22c55e" /> Your Details</h2>
          {error && <div className="alert alert-danger" style={{ background: '#3d3d3d', color: '#27AE60', border: '1px solid #27AE60' }}>{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="floating-grid">
              <div className={`floating-field ${form.age ? 'has-value' : ''}`}>
                <UserRound size={16} className="field-icon" />
                <input type="number" min="1" max="120" value={form.age} onChange={e => set('age', e.target.value)} required />
                <label>Age (years)</label>
              </div>
              <div className={`floating-field ${form.weight ? 'has-value' : ''}`}>
                <Scale size={16} className="field-icon" />
                <input type="number" min="1" value={form.weight} onChange={e => set('weight', e.target.value)} required />
                <label>Weight (kg)</label>
              </div>
              <div className={`floating-field ${form.height ? 'has-value' : ''}`}>
                <Ruler size={16} className="field-icon" />
                <input type="number" min="1" value={form.height} onChange={e => set('height', e.target.value)} required />
                <label>Height (cm)</label>
              </div>
              <div className={`floating-field ${form.bodyfat ? 'has-value' : ''}`}>
                <Scale size={16} className="field-icon" />
                <input type="number" step="0.1" value={form.bodyfat} onChange={e => set('bodyfat', e.target.value)} />
                <label>Body Fat % (optional)</label>
              </div>
            </div>

            {bfPreview && !form.bodyfat && <small style={{ color: '#94a3b8' }}>Auto-calculated preview: ~{bfPreview}%</small>}

            <div style={{ marginTop: 18, marginBottom: 16 }}>
              <label style={{ display: 'block', marginBottom: 6 }}>Gender</label>
              <div className="toggle-pill">
                <div className={`toggle-pill__slider ${form.gender === 'female' ? 'female' : ''}`} />
                <button type="button" onClick={() => set('gender', 'male')}>Male</button>
                <button type="button" onClick={() => set('gender', 'female')}>Female</button>
              </div>
            </div>

            <div className="floating-grid">
              <div className={`floating-field ${form.goal ? 'has-value' : ''}`}>
                <Leaf size={16} className="field-icon" />
                <select value={form.goal} onChange={e => set('goal', e.target.value)}>
                  <option value="healthy">Maintain / Stay Healthy</option>
                  <option value="weight loss">Weight Loss</option>
                  <option value="weight gain">Weight Gain</option>
                </select>
                <label>Goal</label>
              </div>

              <div className={`floating-field ${form.activity ? 'has-value' : ''}`}>
                <Leaf size={16} className="field-icon" />
                <select value={form.activity} onChange={e => set('activity', e.target.value)}>
                  <option value="Very Light">Very Light (sedentary)</option>
                  <option value="Light">Light (1-3 days/week)</option>
                  <option value="Heavy">Moderate (3-5 days/week)</option>
                  <option value="Very Heavy">Very Heavy (6-7 days/week)</option>
                </select>
                <label>Activity Level</label>
              </div>

              <div className={`floating-field ${form.planPeriod ? 'has-value' : ''}`}>
                <Calendar size={16} className="field-icon" />
                <select value={form.planPeriod} onChange={e => set('planPeriod', e.target.value)}>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
                <label>Plan Period</label>
              </div>

              <div className={`floating-field ${form.planDate ? 'has-value' : ''}`}>
                <Calendar size={16} className="field-icon" />
                <input type="date" value={form.planDate} onChange={e => set('planDate', e.target.value)} required />
                <label>Plan Start Date</label>
              </div>
            </div>

            <div className={`floating-field ${form.reminderTime ? 'has-value' : ''}`} style={{ marginTop: 14 }}>
              <Clock3 size={16} className="field-icon" />
              <input type="time" value={form.reminderTime} onChange={e => set('reminderTime', e.target.value)} />
              <label>Reminder Time</label>
            </div>

            <motion.button whileTap={{ scale: 0.97 }} type="submit" className="btn-green shimmer-btn w-100" style={{ marginTop: 18, minHeight: 56 }} disabled={loading || !form.gender}>
              <AnimatePresence mode="wait">
                {loading ? (
                  <motion.span key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    <span className="spinner-border spinner-border-sm me-2" role="status"></span>Generating Plan...
                  </motion.span>
                ) : (
                  <motion.span key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    Get My Diet Plan
                  </motion.span>
                )}
              </AnimatePresence>
            </motion.button>
          </form>
        </GlassCard>
      </div>
    </motion.main>
  );
}
