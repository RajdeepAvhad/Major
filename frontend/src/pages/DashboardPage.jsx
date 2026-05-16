import React, { useEffect, useState } from 'react';
import { apiGet } from '../api/client';
import StreakCard from '../components/dashboard/StreakCard';
import CalorieAdherenceChart from '../components/dashboard/CalorieAdherenceChart';
import QuickStatsCard from '../components/dashboard/QuickStatsCard';
import RecentDietsWidget from '../components/dashboard/RecentDietsWidget';
import './DashboardPage.css';

const DashboardPage = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await apiGet('/api/diet-insights/');
        if (response.ok) {
          setDashboardData(response);
        } else {
          setError(response.message || 'Failed to load dashboard data');
        }
      } catch (err) {
        setError(err.message || 'Error loading dashboard');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-container">
          <h1 className="dashboard-title">📊 Dashboard</h1>
          <div className="loading-skeleton">
            <div className="skeleton-card" />
            <div className="skeleton-card" />
            <div className="skeleton-card" />
            <div className="skeleton-card" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-container">
          <h1 className="dashboard-title">📊 Dashboard</h1>
          <div className="error-message">
            <p>⚠️ {error}</p>
            <p className="error-hint">Please try again later</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-container">
        <div className="dashboard-header">
          <h1 className="dashboard-title">📊 Your Progress Dashboard</h1>
          <p className="dashboard-subtitle">Track your nutrition and diet consistency</p>
        </div>

        <div className="dashboard-grid">
          {/* Streak Card - Top Left */}
          <div className="grid-item span-1">
            <StreakCard streakDays={dashboardData?.streak_days || 0} />
          </div>

          {/* Quick Stats - Top Right */}
          <div className="grid-item span-1">
            <QuickStatsCard
              totalDiets={dashboardData?.total_diets || 0}
              avgAdherence={dashboardData?.avg_calorie_adherence || 0}
              stats={dashboardData?.stats || {}}
            />
          </div>

          {/* Calorie Adherence Chart - Full Width */}
          <div className="grid-item span-2">
            <CalorieAdherenceChart weeklyTrend={dashboardData?.weekly_trend || []} />
          </div>

          {/* Recent Diets - Bottom */}
          <div className="grid-item span-2">
            <RecentDietsWidget lastDiets={dashboardData?.recent_diets || []} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
