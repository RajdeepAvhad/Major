import React from 'react';
import './QuickStatsCard.css';

const QuickStatsCard = ({ totalDiets = 0, avgAdherence = 0, stats = {} }) => {
  const formatStatValue = (value) => {
    if (typeof value === 'number') {
      return Math.round(value);
    }
    return value || '—';
  };

  return (
    <div className="quick-stats-card">
      <h3 className="stats-title">📈 Quick Stats</h3>

      <div className="stats-grid">
        <div className="stat-item">
          <div className="stat-icon">📋</div>
          <div className="stat-info">
            <p className="stat-label">Total Plans</p>
            <p className="stat-value">{totalDiets}</p>
          </div>
        </div>

        <div className="stat-item">
          <div className="stat-icon">✓</div>
          <div className="stat-info">
            <p className="stat-label">Avg Adherence</p>
            <p className="stat-value">{formatStatValue(avgAdherence)}%</p>
          </div>
        </div>

        <div className="stat-item">
          <div className="stat-icon">❤️</div>
          <div className="stat-info">
            <p className="stat-label">Favorite Food</p>
            <p className="stat-value stat-food">
              {stats.most_selected_food ? stats.most_selected_food.substring(0, 12) : '—'}
            </p>
          </div>
        </div>

        <div className="stat-item">
          <div className="stat-icon">🕐</div>
          <div className="stat-info">
            <p className="stat-label">Most Active</p>
            <p className="stat-value">
              {stats.preferred_time
                ? stats.preferred_time.charAt(0).toUpperCase() + stats.preferred_time.slice(1)
                : '—'}
            </p>
          </div>
        </div>
      </div>

      <div className="adherence-bar">
        <div className="adherence-label">
          <span>Adherence Goal</span>
          <span className="adherence-percent">{formatStatValue(avgAdherence)}%</span>
        </div>
        <div className="adherence-track">
          <div
            className={`adherence-fill ${
              avgAdherence >= 90 ? 'excellent' : avgAdherence >= 80 ? 'good' : 'needs-work'
            }`}
            style={{ width: `${Math.min(avgAdherence, 100)}%` }}
          />
        </div>
      </div>
    </div>
  );
};

export default QuickStatsCard;
