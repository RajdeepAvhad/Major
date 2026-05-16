import React from 'react';
import './MacroBreakdown.css';

const MacroBreakdown = ({ selectedMacros, targetCalories, targetProtein = 50, targetFat = 65, targetCarbs = 300 }) => {
  const calculatePercentage = (actual, target) => {
    if (!target) return 0;
    return Math.round((actual / target) * 100);
  };

  const getColorClass = (actual, target) => {
    const percentage = calculatePercentage(actual, target);
    if (percentage >= 90 && percentage <= 110) return 'macro-bar-good';
    if (percentage >= 80 && percentage <= 120) return 'macro-bar-warning';
    return 'macro-bar-danger';
  };

  const MacroBar = ({ label, actual, target, unit = 'cal' }) => {
    const percentage = calculatePercentage(actual, target);
    const colorClass = getColorClass(actual, target);
    const displayActual = Math.round(actual);
    const displayTarget = Math.round(target);

    return (
      <div className="macro-bar-container">
        <div className="macro-header">
          <span className="macro-label">{label}</span>
          <span className="macro-value">
            {displayActual} / {displayTarget} {unit}
          </span>
        </div>
        <div className="macro-bar-background">
          <div
            className={`macro-bar-fill ${colorClass}`}
            style={{ width: `${Math.min(percentage, 100)}%` }}
          >
            <span className="macro-bar-percentage">{percentage}%</span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="macro-breakdown">
      <h3 className="macro-title">📊 Nutrition Breakdown</h3>
      <div className="macros-grid">
        <MacroBar
          label="Calories"
          actual={selectedMacros.cal}
          target={targetCalories}
          unit="kcal"
        />
        <MacroBar
          label="Protein"
          actual={selectedMacros.pro}
          target={targetProtein}
          unit="g"
        />
        <MacroBar
          label="Fat"
          actual={selectedMacros.fat}
          target={targetFat}
          unit="g"
        />
        <MacroBar
          label="Carbs"
          actual={selectedMacros.carbs}
          target={targetCarbs}
          unit="g"
        />
      </div>
    </div>
  );
};

export default MacroBreakdown;
