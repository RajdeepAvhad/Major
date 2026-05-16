import { useEffect, useState } from 'react';
import { useAuth } from '../api/AuthContext';
import { apiGet } from '../api/client';
import { Link } from 'react-router-dom';

export default function ProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [preferences, setPreferences] = useState(null);
  const [insights, setInsights] = useState(null);
  const [waterToday, setWaterToday] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiGet('/api/user/profile/'),
      apiGet('/api/preferences/'),
      apiGet('/api/diet-insights/'),
      apiGet('/api/water/'),
    ])
      .then(([profileRes, prefRes, insightRes, waterRes]) => {
        if (profileRes.ok) setProfile(profileRes.user);
        if (prefRes.ok) setPreferences(prefRes.preferences);
        if (insightRes.ok) setInsights(insightRes.insights);
        if (waterRes.ok) setWaterToday(waterRes.today);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="spinner-wrap"><div className="spinner-border"></div></div>;

  if (!user) return (
    <div className="text-center py-5">
      <p>Please <Link to="/login">login</Link> to view your profile.</p>
    </div>
  );

  return (
    <>
      <div className="page-banner">
        <h1>My Profile</h1>
        <p>Welcome back, {user.username}!</p>
      </div>

      <div className="container py-5" style={{ maxWidth: 600 }}>
        {insights && (
          <div className="card shadow-sm mb-4">
            <div className="card-header" style={{ background: '#2ECC71', color: '#2c2c2c' }}>
              <h5 className="mb-0">My Dashboard</h5>
            </div>
            <div className="card-body" style={{ display: 'grid', gap: 10 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Total Plans</span>
                <strong>{insights.total_plans}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Current Streak</span>
                <strong>{insights.current_streak} days</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Longest Streak</span>
                <strong>{insights.longest_streak} days</strong>
              </div>
              {waterToday && (
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Water Today</span>
                  <strong>{waterToday.amount_ml} ml</strong>
                </div>
              )}
              {insights.badges?.length > 0 && (
                <div>
                  <div style={{ fontSize: 12, color: '#777', marginBottom: 6 }}>Badges</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {insights.badges.map((b, i) => (
                      <span key={i} style={{ border: '1px solid #2ECC71', color: '#2ECC71', borderRadius: 12, padding: '2px 10px', fontSize: 12 }}>
                        {b.title}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        <div className="card shadow-sm">
          <div className="card-header" style={{ background: '#2ECC71', color: '#2c2c2c' }}>
            <h5 className="mb-0">Account Information</h5>
          </div>
          <div className="card-body">
            <table className="table table-borderless mb-0">
              <tbody>
                <tr>
                  <th style={{ width: '35%', color: '#2ECC71' }}>Username</th>
                  <td>{profile?.username || user.username}</td>
                </tr>
                <tr>
                  <th style={{ color: '#2ECC71' }}>Email</th>
                  <td>{profile?.email || user.email}</td>
                </tr>
                {profile?.date_joined && (
                  <tr>
                    <th style={{ color: '#2ECC71' }}>Member Since</th>
                    <td>{new Date(profile.date_joined).toLocaleDateString('en-IN', { dateStyle: 'long' })}</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {preferences && (
          <div className="card shadow-sm mt-4">
            <div className="card-header" style={{ background: '#2ECC71', color: '#2c2c2c' }}>
              <h5 className="mb-0">Saved Preferences</h5>
            </div>
            <div className="card-body">
              <table className="table table-borderless mb-0">
                <tbody>
                  <tr>
                    <th style={{ width: '35%', color: '#2ECC71' }}>Goal</th>
                    <td>{preferences.goal}</td>
                  </tr>
                  <tr>
                    <th style={{ color: '#2ECC71' }}>Activity</th>
                    <td>{preferences.activity}</td>
                  </tr>
                  <tr>
                    <th style={{ color: '#2ECC71' }}>Plan Period</th>
                    <td>{preferences.plan_period}</td>
                  </tr>
                  {preferences.plan_date && (
                    <tr>
                      <th style={{ color: '#2ECC71' }}>Start Date</th>
                      <td>{preferences.plan_date}</td>
                    </tr>
                  )}
                  {preferences.reminder_time && (
                    <tr>
                      <th style={{ color: '#2ECC71' }}>Reminder</th>
                      <td>{preferences.reminder_time}</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        <div className="d-flex gap-3 mt-4">
          <Link to="/diet-history" className="btn-brand">View Diet History</Link>
          <Link to="/dietplanner" className="btn-brand" style={{ background: '#28a745' }}>Plan My Diet</Link>
        </div>
      </div>
    </>
  );
}
