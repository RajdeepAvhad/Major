import React from 'react';
import './RecentDietsWidget.css';

const RecentDietsWidget = ({ lastDiets = [] }) => {
  const formatDate = (dateString) => {
    if (!dateString) return '—';
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });
    } catch {
      return '—';
    }
  };

  const getAdherenceColor = (selected, target) => {
    if (target === 0) return 'neutral';
    const percentage = (selected / target) * 100;
    if (percentage >= 90 && percentage <= 110) return 'good';
    if (percentage >= 80 && percentage <= 120) return 'warning';
    return 'needs-work';
  };

  if (!lastDiets || lastDiets.length === 0) {
    return (
      <div className="recent-diets-widget">
        <h3 className="widget-title">📋 Recent Diet Plans</h3>
        <div className="empty-state">
          <p>No diet plans saved yet</p>
          <p className="empty-hint">Start creating your first diet plan to see them here!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="recent-diets-widget">
      <h3 className="widget-title">📋 Recent Diet Plans</h3>

      <div className="diets-list">
        {lastDiets.slice(0, 5).map((diet, idx) => (
          <div key={idx} className="diet-item">
            <div className="diet-header">
              <span className="diet-date">📅 {formatDate(diet.created_at || diet.plan_date)}</span>
              <span className={`diet-period badge-${diet.period || 'daily'}`}>
                {(diet.period || 'daily').charAt(0).toUpperCase() + (diet.period || 'daily').slice(1)}
              </span>
            </div>

            <div className="diet-details">
              <div className="diet-detail-item">
                <span className="detail-label">Calories</span>
                <span className="detail-value">
                  {diet.selected_calories || 0} / {diet.target_calories || 0}
                </span>
              </div>

              <div className="diet-detail-item">
                <span className="detail-label">BMI</span>
                <span className="detail-value">{diet.bmi ? diet.bmi.toFixed(1) : '—'}</span>
              </div>

              <div className="diet-detail-item">
                <span className="detail-label">Body Fat</span>
                <span className="detail-value">{diet.bodyfat ? diet.bodyfat.toFixed(1) : '—'}%</span>
              </div>
            </div>

            <div className="diet-adherence">
              <div className="adherence-label">Adherence</div>
              <div className="adherence-track">
                <div
                  className={`adherence-fill ${getAdherenceColor(
                    diet.selected_calories || 0,
                    diet.target_calories || 1
                  )}`}
                  style={{
                    width: `${Math.min(
                      ((diet.selected_calories || 0) / (diet.target_calories || 1)) * 100,
                      100
                    )}%`,
                  }}
                />
              </div>
              <span className="adherence-percent">
                {diet.target_calories
                  ? Math.round(((diet.selected_calories || 0) / diet.target_calories) * 100)
                  : 0}
                %
              </span>
            </div>
          </div>
        ))}
      </div>

      {lastDiets.length > 5 && (
        <button className="view-all-btn">
          View All {lastDiets.length} Diet Plans →
        </button>
      )}
    </div>
  );
};

export default RecentDietsWidget;
