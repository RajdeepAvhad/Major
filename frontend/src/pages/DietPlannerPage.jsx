import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiGet, apiPost } from '../api/client';

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
    <>
      <div className="page-banner">
        <h1>Diet Planner</h1>
        <p>Enter your body metrics and we'll recommend a personalised meal plan.</p>
      </div>

      <div className="planner-form">
        <h2>Your Details</h2>
        {error && <div className="alert alert-danger" style={{ background: '#3d3d3d', color: '#27AE60', border: '1px solid #27AE60' }}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="row g-3">
            <div className="col-6">
              <label className="form-label" style={{ color: '#e8e8e8' }}>Age (years)</label>
              <input type="number" className="form-control" min="1" max="120" value={form.age}
                onChange={e => set('age', e.target.value)} required placeholder="e.g. 22"
                style={{ background: '#3d3d3d', color: '#e8e8e8', border: '1px solid #555' }} />
            </div>
            <div className="col-6">
              <label className="form-label" style={{ color: '#e8e8e8' }}>Weight (kg)</label>
              <input type="number" className="form-control" min="1" value={form.weight}
                onChange={e => set('weight', e.target.value)} required placeholder="e.g. 70"
                style={{ background: '#3d3d3d', color: '#e8e8e8', border: '1px solid #555' }} />
            </div>
            <div className="col-6">
              <label className="form-label" style={{ color: '#e8e8e8' }}>Height (cm)</label>
              <input type="number" className="form-control" min="1" value={form.height}
                onChange={e => set('height', e.target.value)} required placeholder="e.g. 170"
                style={{ background: '#3d3d3d', color: '#e8e8e8', border: '1px solid #555' }} />
            </div>
            <div className="col-6">
              <label className="form-label" style={{ color: '#e8e8e8' }}>Body Fat % <small style={{ color: '#999' }}>(optional)</small></label>
              <input type="number" className="form-control" step="0.1" value={form.bodyfat}
                onChange={e => set('bodyfat', e.target.value)} placeholder="Leave blank to auto-calculate"
                style={{ background: '#3d3d3d', color: '#e8e8e8', border: '1px solid #555' }} />
              {bfPreview && !form.bodyfat && (
                <small style={{ color: '#999' }}>Auto-calculated: ~{bfPreview}%</small>
              )}
            </div>

            <div className="col-12">
              <label className="form-label" style={{ color: '#e8e8e8' }}>Gender</label>
              <div className="d-flex gap-3">
                {['male', 'female'].map(g => (
                  <label key={g} style={{ cursor: 'pointer', fontWeight: form.gender === g ? 700 : 400, color: '#e8e8e8' }}>
                    <input type="radio" name="gender" value={g} checked={form.gender === g}
                      onChange={() => set('gender', g)} style={{ marginRight: 6 }} />
                    {g.charAt(0).toUpperCase() + g.slice(1)}
                  </label>
                ))}
              </div>
            </div>

            <div className="col-12">
              <label className="form-label" style={{ color: '#e8e8e8' }}>Goal</label>
              <select className="form-select" value={form.goal} onChange={e => set('goal', e.target.value)}
                style={{ background: '#3d3d3d', color: '#e8e8e8', border: '1px solid #555' }}>
                <option value="healthy">Maintain / Stay Healthy</option>
                <option value="weight loss">Weight Loss</option>
                <option value="weight gain">Weight Gain</option>
              </select>
            </div>

            <div className="col-12">
              <label className="form-label" style={{ color: '#e8e8e8' }}>Activity Level</label>
              <select className="form-select" value={form.activity} onChange={e => set('activity', e.target.value)}
                style={{ background: '#3d3d3d', color: '#e8e8e8', border: '1px solid #555' }}>
                <option value="Very Light">Very Light (sedentary)</option>
                <option value="Light">Light (1-3 days/week)</option>
                <option value="Heavy">Moderate (3-5 days/week)</option>
                <option value="Very Heavy">Very Heavy (6-7 days/week)</option>
              </select>
            </div>

            <div className="col-6">
              <label className="form-label" style={{ color: '#e8e8e8' }}>Plan Period</label>
              <select className="form-select" value={form.planPeriod} onChange={e => set('planPeriod', e.target.value)}
                style={{ background: '#3d3d3d', color: '#e8e8e8', border: '1px solid #555' }}>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>

            <div className="col-6">
              <label className="form-label" style={{ color: '#e8e8e8' }}>Plan Start Date</label>
              <input
                type="date"
                className="form-control"
                value={form.planDate}
                onChange={e => set('planDate', e.target.value)}
                required
                style={{ background: '#3d3d3d', color: '#e8e8e8', border: '1px solid #555' }}
              />
            </div>

            <div className="col-6">
              <label className="form-label" style={{ color: '#e8e8e8' }}>Reminder Time</label>
              <input
                type="time"
                className="form-control"
                value={form.reminderTime}
                onChange={e => set('reminderTime', e.target.value)}
                style={{ background: '#3d3d3d', color: '#e8e8e8', border: '1px solid #555' }}
              />
            </div>

            <div className="col-12 mt-3">
              <button type="submit" className="btn-brand w-100" style={{ fontSize: 16 }} disabled={loading || !form.gender}>
                {loading ? (
                  <><span className="spinner-border spinner-border-sm me-2" role="status"></span>Analysing…</>
                ) : 'Get My Diet Plan'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </>
  );
}
