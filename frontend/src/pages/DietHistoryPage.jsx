import { useEffect, useState } from 'react';
import {
  AreaChart, Area, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { apiGet, apiPost } from '../api/client';
import { Link } from 'react-router-dom';

function formatDate(iso) {
  return new Date(iso).toLocaleString('en-IN', {
    dateStyle: 'medium', timeStyle: 'short',
  });
}

function shortDate(iso) {
  const d = new Date(iso);
  return `${d.getDate()}/${d.getMonth() + 1}`;
}

function TrendCharts({ history }) {
  if (history.length < 1) return null;

  // Sort oldest-first for charts
  const sorted = [...history].sort((a, b) => new Date(a.created_at) - new Date(b.created_at));

  const calData = sorted.map(r => ({
    date: shortDate(r.created_at),
    Target: r.target_calories,
    Consumed: r.selected_calories,
  }));

  const bmiData = sorted
    .filter(r => r.bmi)
    .map(r => ({ date: shortDate(r.created_at), BMI: r.bmi }));

  return (
    <div className="trend-charts-wrap">
      <h5 style={{ color: '#2ECC71', marginBottom: 16 }}>Calorie Trend</h5>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={calData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="colTarget" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#2ECC71" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#2ECC71" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colConsumed" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#82ca9d" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#82ca9d" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip formatter={(v, name) => [`${v} kcal`, name]} />
          <Area type="monotone" dataKey="Target"   stroke="#2ECC71" fill="url(#colTarget)"   dot={{ r: 4 }} />
          <Area type="monotone" dataKey="Consumed" stroke="#82ca9d" fill="url(#colConsumed)" dot={{ r: 4 }} />
        </AreaChart>
      </ResponsiveContainer>

      {bmiData.length >= 1 && (
        <>
          <h5 style={{ color: '#2ECC71', margin: '20px 0 12px' }}>BMI Trend</h5>
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={bmiData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} domain={['auto', 'auto']} />
              <Tooltip formatter={v => [`${v}`, 'BMI']} />
              <Line type="monotone" dataKey="BMI" stroke="#2ECC71" strokeWidth={2} dot={{ r: 5, fill: '#2ECC71' }} />
            </LineChart>
          </ResponsiveContainer>
        </>
      )}
    </div>
  );
}

export default function DietHistoryPage() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState('');
  const [deleting, setDeleting] = useState(null);
  const [trackerPeriod, setTrackerPeriod] = useState('daily');
  const [trackerSummary, setTrackerSummary] = useState([]);
  const [waterToday, setWaterToday] = useState({ date: '', amount_ml: 0 });
  const [waterHistory, setWaterHistory] = useState([]);

  useEffect(() => {
    apiGet('/api/diet-history/')
      .then(res => {
        if (res.ok) setHistory(res.history);
        else setError('Could not load history.');
      })
      .catch(() => setError('Network error.'))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    apiGet(`/api/diet-tracker/?period=${trackerPeriod}`)
      .then(res => {
        if (res.ok) setTrackerSummary(res.summary);
      })
      .catch(() => setTrackerSummary([]));
  }, [trackerPeriod]);

  useEffect(() => {
    apiGet('/api/water/')
      .then(res => {
        if (res.ok) {
          setWaterToday(res.today);
          setWaterHistory(res.history || []);
        }
      })
      .catch(() => {});
  }, []);

  const updateWater = async (delta) => {
    const res = await apiPost('/api/water/update/', { delta_ml: delta });
    if (res.ok) {
      setWaterToday({ date: res.date, amount_ml: res.amount_ml });
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this diet record?')) return;
    setDeleting(id);
    try {
      const res = await fetch(`/api/diet-history/${id}/delete/`, {
        method: 'DELETE',
        headers: { 'X-CSRFToken': document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '' },
        credentials: 'include',
      });
      if (res.ok) {
        setHistory(prev => prev.filter(r => r.id !== id));
      } else {
        alert('Could not delete this record.');
      }
    } catch {
      alert('Network error while deleting.');
    }
    setDeleting(null);
  };

  if (loading) return <div className="spinner-wrap"><div className="spinner-border"></div></div>;

  return (
    <>
      <div className="page-banner">
        <h1>Diet History</h1>
        <p>Your previously saved diet plans and health trends.</p>
      </div>

      <div className="container py-4" style={{ maxWidth: 860 }}>
        {error && <div className="alert alert-danger">{error}</div>}

        {history.length === 0 && !error && (
          <div className="text-center py-5">
            <p className="text-muted">No saved diets yet.</p>
            <Link to="/dietplanner" className="btn-brand">Plan My Diet</Link>
          </div>
        )}

        {history.length > 0 && <TrendCharts history={history} />}

        {history.length > 0 && (
          <div className="history-card" style={{ marginTop: 24 }}>
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h5 style={{ color: '#2ECC71', margin: 0 }}>Tracker Summary</h5>
              <select
                className="form-select"
                style={{ width: 160 }}
                value={trackerPeriod}
                onChange={e => setTrackerPeriod(e.target.value)}
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
            {trackerSummary.length === 0 && (
              <p className="text-muted" style={{ marginBottom: 0 }}>No tracker data yet.</p>
            )}
            {trackerSummary.length > 0 && (
              <div style={{ display: 'grid', gap: 10 }}>
                {trackerSummary.map(row => (
                  <div key={row.key} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 14 }}>
                    <span style={{ color: '#aaa' }}>{row.key}</span>
                    <span style={{ color: '#2ECC71', fontWeight: 600 }}>
                      {row.selected_calories} / {row.target_calories} kcal
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="history-card">
          <div className="d-flex justify-content-between align-items-center mb-2">
            <h5 style={{ color: '#2ECC71', margin: 0 }}>Water Tracker</h5>
            <span style={{ fontSize: 13, color: '#777' }}>{waterToday.date || 'Today'}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontWeight: 600 }}>{waterToday.amount_ml} ml</div>
              <div style={{ fontSize: 12, color: '#777' }}>Goal: 2000 ml</div>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="btn-brand" style={{ padding: '4px 10px', fontSize: 12 }} onClick={() => updateWater(250)}>+250 ml</button>
              <button className="btn-brand" style={{ padding: '4px 10px', fontSize: 12 }} onClick={() => updateWater(500)}>+500 ml</button>
            </div>
          </div>
          {waterHistory.length > 0 && (
            <div style={{ marginTop: 10, display: 'grid', gap: 6 }}>
              {waterHistory.map(row => (
                <div key={row.date} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: '#666' }}>
                  <span>{row.date}</span>
                  <span>{row.amount_ml} ml</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {history.length > 0 && (
          <h5 style={{ color: '#aaa', margin: '24px 0 12px' }}>
            All Saved Plans &nbsp;
            <span style={{ color: '#aaa', fontSize: 13, fontWeight: 400 }}>({history.length} records)</span>
          </h5>
        )}

        {history.map(record => (
          <div key={record.id} className="history-card" style={{ position: 'relative' }}>
            <div className="d-flex justify-content-between align-items-center mb-2">
              <div className="date">
                {formatDate(record.created_at)}
                {record.plan_date && (
                  <span style={{ color: '#999', fontSize: 12, marginLeft: 8 }}>
                    Plan: {record.plan_date} ({record.period || 'daily'})
                  </span>
                )}
              </div>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <span style={{
                  background: '#2ECC71', color: '#2c2c2c', borderRadius: 20,
                  padding: '3px 12px', fontSize: 13,
                }}>
                  {record.selected_calories} / {record.target_calories} kcal
                </span>
                <button
                  onClick={() => handleDelete(record.id)}
                  disabled={deleting === record.id}
                  title="Delete this record"
                  style={{
                    background: 'none', border: '1px solid #e00', color: '#e00',
                    borderRadius: 6, padding: '2px 8px', cursor: 'pointer', fontSize: 13,
                    opacity: deleting === record.id ? 0.5 : 1,
                  }}
                >
                  {deleting === record.id ? '…' : '✕'}
                </button>
              </div>
            </div>

            {record.bmiinfo && <p style={{ color: '#aaa', fontSize: 14 }}>{record.bmiinfo}</p>}

            <div style={{ display: 'flex', gap: 20, fontSize: 13, marginBottom: 6 }}>
              {record.bmi    != null && <span>BMI: <strong>{record.bmi}</strong></span>}
              {record.bodyfat != null && <span>Body Fat: <strong>{record.bodyfat}%</strong></span>}
            </div>

            {record.items.length > 0 && (
              <div className="mt-2">
                <strong style={{ fontSize: 13 }}>Selected Foods:</strong>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 6 }}>
                  {record.items.map((item, i) => (
                    <span key={i} style={{
                      background: '#3d3d3d', border: '1px solid #2ECC71',
                      color: '#2ECC71', borderRadius: 12, padding: '2px 10px', fontSize: 12,
                    }}>
                      {item.name} ({item.meal}, {item.calories} kcal)
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </>
  );
}
