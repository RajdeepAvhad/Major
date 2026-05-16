import React from 'react';
import './StreakCard.css';

const StreakCard = ({ streakDays = 0 }) => {
  const getStreakMessage = (days) => {
    if (days === 0) return 'Start your first diet plan!';
    if (days === 1) return 'Great start!';
    if (days < 7) return 'Keep it going!';
    if (days < 30) return 'Amazing consistency!';
    return 'Outstanding dedication!';
  };

  const getStreakColor = (days) => {
    if (days === 0) return 'gray';
    if (days < 3) return 'blue';
    if (days < 7) return 'orange';
    if (days < 30) return 'green';
    return 'gold';
  };

  return (
    <div className={`streak-card streak-${getStreakColor(streakDays)}`}>
      <div className="streak-icon">🔥</div>
      <div className="streak-content">
        <h3 className="streak-number">{streakDays}</h3>
        <p className="streak-label">Day Streak</p>
        <p className="streak-message">{getStreakMessage(streakDays)}</p>
      </div>
      {streakDays > 0 && (
        <div className="streak-badge">
          <span className="badge-text">
            {Math.floor(streakDays / 7)} weeks
          </span>
        </div>
      )}
    </div>
  );
};

export default StreakCard;
