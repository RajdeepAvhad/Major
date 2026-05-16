import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './CalorieAdherenceChart.css';

const CalorieAdherenceChart = ({ weeklyTrend = [] }) => {
  // Transform data for the chart
  const chartData = weeklyTrend.map((day) => ({
    date: new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' }),
    actual: day.cal || 0,
    target: day.target || 2000,
    adherence: day.adherence || 0,
  }));

  // Ensure we have 7 days of data
  const fillData = (data) => {
    if (data.length === 0) {
      return Array.from({ length: 7 }, (_, i) => ({
        date: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i],
        actual: 0,
        target: 2000,
        adherence: 0,
      }));
    }
    return data;
  };

  const dataToDisplay = fillData(chartData);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="chart-tooltip">
          <p className="tooltip-date">{data.date}</p>
          <p className="tooltip-actual">Consumed: {data.actual} kcal</p>
          <p className="tooltip-target">Target: {data.target} kcal</p>
          <p className="tooltip-adherence">Adherence: {data.adherence}%</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="calorie-chart-card">
      <h3 className="chart-title">📈 7-Day Calorie Trend</h3>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={dataToDisplay}>
            <defs>
              <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2ECC71" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#2ECC71" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorTarget" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3498DB" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#3498DB" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#444" />
            <XAxis dataKey="date" stroke="#aaa" />
            <YAxis stroke="#aaa" />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line
              type="monotone"
              dataKey="actual"
              stroke="#2ECC71"
              dot={{ fill: '#2ECC71', r: 5 }}
              activeDot={{ r: 7 }}
              name="Consumed"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorActual)"
            />
            <Line
              type="monotone"
              dataKey="target"
              stroke="#3498DB"
              dot={{ fill: '#3498DB', r: 4 }}
              activeDot={{ r: 6 }}
              name="Target"
              strokeWidth={2}
              strokeDasharray="5 5"
              fill="url(#colorTarget)"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-info">
        <div className="info-item">
          <span className="info-icon">✓</span>
          <span className="info-text">Green line shows your actual calorie intake</span>
        </div>
        <div className="info-item">
          <span className="info-icon">—</span>
          <span className="info-text">Blue dashed line shows your daily target</span>
        </div>
        <div className="info-item">
          <span className="info-icon">💡</span>
          <span className="info-text">Hover over the chart for detailed information</span>
        </div>
      </div>
    </div>
  );
};

export default CalorieAdherenceChart;
