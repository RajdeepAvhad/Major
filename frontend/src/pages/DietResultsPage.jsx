import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import FoodCard from '../components/FoodCard';
import MacroBreakdown from '../components/MacroBreakdown';
import FavoriteFoodsPanel from '../components/FavoriteFoodsPanel';
import ShoppingListModal from '../components/ShoppingListModal';
import ToastContainer, { useToast } from '../utils/Toast';
import { apiGet, apiPost } from '../api/client';

const MACRO_COLORS = {
  Protein: '#2ECC71',
  Fat:     '#ffc658',
  Carbs:   '#82ca9d',
};

export default function DietResultsPage() {
  const navigate = useNavigate();
  const { toasts, addToast, removeToast } = useToast();
  const [results, setResults] = useState(null);
  const [selected, setSelected] = useState({}); // key: `${meal}-${id}` -> food obj
  const [saved, setSaved]       = useState(false);
  const [saving, setSaving]     = useState(false);
  const [favorites, setFavorites] = useState([]);
  const [shoppingListData, setShoppingListData] = useState(null);
  const [showShoppingList, setShowShoppingList] = useState(false);
  const [selectedMacros, setSelectedMacros] = useState({ cal: 0, pro: 0, fat: 0, carbs: 0 });

  useEffect(() => {
    const stored = sessionStorage.getItem('dietResults');
    if (stored) setResults(JSON.parse(stored));
    else navigate('/dietplanner');
  }, []);

  useEffect(() => {
    apiGet('/api/favorites/')
      .then(res => {
        if (res.ok) {
          const normalized = (res.favorites || []).map(f => ({ ...f, id: f.food_id || f.id }));
          setFavorites(normalized);
        }
      })
      .catch(() => {});
  }, []);

  // Calculate macros whenever selected foods change
  useEffect(() => {
    const calculateMacros = () => {
      const foods = Object.values(selected);
      let cal = 0, pro = 0, fat = 0, carbs = 0;

      foods.forEach(food => {
        cal += food.cal || 0;
        pro += food.pro || 0;
        fat += food.fat || 0;
        // Carbs = (Total Calories - (Protein×4 + Fat×9)) / 4
        carbs += Math.max(0, (food.cal - (food.pro * 4 + food.fat * 9)) / 4);
      });

      setSelectedMacros({ cal, pro, fat, carbs });
    };

    calculateMacros();
  }, [selected]);

  if (!results) return (
    <div className="spinner-wrap"><div className="spinner-border"></div></div>
  );

  const totalCal  = Object.values(selected).reduce((s, f) => s + f.cal, 0);
  const targetCal = results.caloriesreq;
  const planPeriod = results.plan_period || 'daily';
  const planDate = results.plan_date || new Date().toISOString().slice(0, 10);
  const periodDays = () => {
    if (planPeriod === 'weekly') return 7;
    if (planPeriod === 'monthly') {
      const d = new Date(planDate);
      return new Date(d.getFullYear(), d.getMonth() + 1, 0).getDate();
    }
    return 1;
  };
  const calStatus = () => {
    if (totalCal === 0) return 'Start by selecting foods using Add This.';
    if (totalCal < targetCal - 50) return 'You are below your calorie target. Add a few more items.';
    if (totalCal <= targetCal + 50) return '✓ Nice! You are within your calorie target range.';
    return 'You are above your calorie target. Remove a few items.';
  };

  const toggle = (food, meal) => {
    const key = `${meal}-${food.id}`;
    setSelected(prev => {
      const copy = { ...prev };
      if (copy[key]) {
        delete copy[key];
        addToast(`Removed ${food.name} from ${meal}`, 'info', 2000);
      } else {
        copy[key] = food;
        addToast(`Added ${food.name} to ${meal}`, 'success', 2000);
      }
      return copy;
    });
  };

  const isChecked = (food, meal) => !!selected[`${meal}-${food.id}`];

  const favoriteIds = new Set(favorites.map(f => f.id));

  const handleToggleFavorite = async (food) => {
    const res = await apiPost('/api/favorites/toggle/', { food_id: food.id });
    if (!res.ok) return;
    setFavorites(prev => {
      const exists = prev.find(f => f.id === food.id);
      if (exists) return prev.filter(f => f.id !== food.id);
      return [{ ...food, id: food.id }, ...prev];
    });
  };

  const quickAdd = (food, meal) => {
    const key = `${meal}-${food.id}`;
    setSelected(prev => (prev[key] ? prev : { ...prev, [key]: food }));
  };

  const handleSave = async () => {
    const items = Object.entries(selected).map(([key, f]) => ({
      name: f.name,
      meal: key.split('-')[0],
      calories: f.cal,
    }));
    if (items.length === 0) {
      addToast('Please select at least one food item before saving.', 'warning');
      return;
    }
    setSaving(true);
    const res = await apiPost('/api/save-diet/', {
      items,
      selected_calories: totalCal,
      target_calories: targetCal,
      period: planPeriod,
      plan_date: planDate,
      bmi: results.bmi,
      bodyfat: results.bodyfat,
      bmiinfo: results.bmiinfo,
    });
    setSaving(false);
    if (res.ok) {
      setSaved(true);
      addToast('Diet plan saved successfully!', 'success');
    } else {
      addToast(res.message || 'Unable to save diet.', 'error');
    }
  };

  const handlePrint = () => {
    const selectedFoods = Object.entries(selected);
    if (selectedFoods.length === 0) { alert('Select some foods first to export your plan.'); return; }

    const byMeal = {};
    selectedFoods.forEach(([key, f]) => {
      const meal = key.split('-')[0];
      if (!byMeal[meal]) byMeal[meal] = [];
      byMeal[meal].push(f);
    });

    const mealHtml = Object.entries(byMeal).map(([meal, foods]) => `
      <h3 style="color:#2ECC71;text-transform:capitalize;margin-top:20px">${meal}</h3>
      <table style="width:100%;border-collapse:collapse;font-size:14px">
        <thead>
          <tr style="background:#2ECC71;color:#2c2c2c">
            <th style="padding:6px 10px;text-align:left">Food</th>
            <th style="padding:6px 10px;text-align:right">Cal</th>
            <th style="padding:6px 10px;text-align:right">Protein(g)</th>
            <th style="padding:6px 10px;text-align:right">Fat(g)</th>
            <th style="padding:6px 10px;text-align:right">Carbs(g)</th>
          </tr>
        </thead>
        <tbody>
          ${foods.map((f, i) => `
            <tr style="background:${i % 2 === 0 ? '#2c2c2c' : '#2c2c2c8f3'}">
              <td style="padding:6px 10px">${f.name}</td>
              <td style="padding:6px 10px;text-align:right">${f.cal}</td>
              <td style="padding:6px 10px;text-align:right">${f.pro}</td>
              <td style="padding:6px 10px;text-align:right">${f.fat}</td>
              <td style="padding:6px 10px;text-align:right">${f.sug}</td>
            </tr>`).join('')}
        </tbody>
      </table>`).join('');

    const win = window.open('', '_blank');
    win.document.write(`<!DOCTYPE html><html><head>
      <title>My EatRight Diet Plan</title>
      <style>body{font-family:sans-serif;padding:30px;max-width:800px;margin:0 auto}
      h1{color:#2ECC71}h2{color:#555}th,td{border-bottom:1px solid #eee}</style>
    </head><body>
      <h1>🥗 My EatRight Diet Plan</h1>
      <p><strong>Generated:</strong> ${new Date().toLocaleString()}</p>
      <h2>Health Metrics</h2>
      <p>BMI: <strong>${results.bmi}</strong> &nbsp;·&nbsp; Body Fat: <strong>${results.bodyfat}%</strong></p>
      <p>${results.bmiinfo}</p>
      <p>Daily calorie target: <strong>${targetCal} kcal</strong> &nbsp;·&nbsp; Your selected: <strong>${totalCal} kcal</strong></p>
      <h2>Diet Plan</h2>
      ${mealHtml}
      <script>window.onload=()=>window.print()</script>
    </body></html>`);
    win.document.close();
  };

  const handleShoppingList = () => {
    const selectedFoods = Object.values(selected);
    if (selectedFoods.length === 0) {
      addToast('Select some foods first to create a shopping list.', 'warning');
      return;
    }

    // For now, create a simple categorized list
    const shoppingList = [
      {
        category: 'All Items',
        items: selectedFoods.map(f => ({
          name: f.name,
          quantity: 1,
          unit: 'serving',
          notes: `${f.cal} kcal`,
        })),
      },
    ];

    setShoppingListData(shoppingList);
    setShowShoppingList(true);
    addToast('Shopping list generated!', 'success');
  };

  const MealSection = ({ label, foods, meal }) => {
    if (!foods || foods.length === 0) return null;
    return (
      <div className="card mb-4">
        <div className="section-heading">{label}</div>
        <div className="card-body">
          <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center' }}>
            {foods.map(f => (
              <FoodCard
                key={f.id}
                food={f}
                meal={meal}
                checked={isChecked(f, meal)}
                onToggle={toggle}
                isFavorite={favoriteIds.has(f.id)}
                onToggleFavorite={handleToggleFavorite}
              />
            ))}
          </div>
        </div>
      </div>
    );
  };

  return (
    <>
      <ToastContainer toasts={toasts} removeToast={removeToast} />
      <ShoppingListModal isOpen={showShoppingList} onClose={() => setShowShoppingList(false)} shoppingList={shoppingListData} />
      <div className="calorie-bar">
        <span>
          Total Calories: <strong style={{ color: '#2ECC71' }}>{totalCal}</strong> / {targetCal} Goal
          <span style={{ color: '#999', marginLeft: 8 }}>({planPeriod})</span>
        </span>
        <span style={{ fontSize: 13, color: totalCal > targetCal + 50 ? '#c00' : '#2ECC71' }}>
          {calStatus()}
        </span>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn-brand" style={{ background: '#2c2c2c', color: '#2ECC71', border: '1px solid #2ECC71' }} onClick={handlePrint}>
            Export Plan
          </button>
          <button className="btn-brand" style={{ background: '#2c2c2c', color: '#2ECC71', border: '1px solid #2ECC71' }} onClick={handleShoppingList}>
            🛒 Shopping List
          </button>
          {saved
            ? <span style={{ color: 'green', fontWeight: 600 }}>✓ Diet Saved!</span>
            : <button className="btn-brand" onClick={handleSave} disabled={saving}>
                {saving ? 'Saving…' : 'Save My Diet'}
              </button>
          }
        </div>
      </div>

      {/* Info Banner */}
      <div className="info-banner">
        {results.bmi > 0 && <h3>BMI: {results.bmi}</h3>}
        {results.bodyfat > 0 && (
          <p style={{ color: '#aaa' }}>
            Body Fat: <strong>{results.bodyfat}%</strong>
            {results.bodyfat_source === 'calculated' && (
              <span style={{ color: '#2ECC71', fontSize: 13 }}> (auto-calculated)</span>
            )}
          </p>
        )}
        <p style={{ fontSize: 17, marginTop: 6 }}>{results.bmiinfo}</p>
        <p style={{ fontWeight: 600, marginTop: 4 }}>
          You should eat <span style={{ color: '#2ECC71' }}>{targetCal}</span> calories per day
          {planPeriod !== 'daily' && (
            <span style={{ color: '#aaa', fontWeight: 400 }}>
              {' '}· Period total: {targetCal * periodDays()} kcal
            </span>
          )}
        </p>
        <p style={{ color: '#777', fontSize: 13, marginTop: 2 }}>
          Plan period: <strong>{planPeriod}</strong> starting {planDate}
        </p>
      </div>

      {/* Macro Chart */}
      <div className="container py-2">
        <MacroBreakdown
          selectedMacros={selectedMacros}
          targetCalories={targetCal}
          targetProtein={Math.max(50, targetCal / 10)}
          targetFat={Math.max(65, targetCal / 30)}
          targetCarbs={Math.max(300, (targetCal * 0.5) / 4)}
        />
      </div>

      {/* Favorites Panel */}
      <div className="container py-2">
        <FavoriteFoodsPanel
          favorites={favorites}
          onAddToMeal={(meal, food) => quickAdd(food, meal)}
        />
      </div>

      {/* Food Sections */}
      <div className="container py-3">
        <div className="card mb-4">
          <div className="card-header" style={{ background: '#2ECC71' }}>
            <h4 className="m-0 text-white text-center">Choose Your Diet Plan</h4>
          </div>
          <div className="card-body">
            <MealSection label="🌅 Breakfast" foods={results.breakfast} meal="breakfast" />
            <MealSection label="☀️ Lunch"     foods={results.lunch}     meal="lunch" />
            <MealSection label="🌙 Dinner"    foods={results.dinner}    meal="dinner" />
          </div>
        </div>

        <div className="text-center mb-5">
          {saved
            ? <a href="/diet-history" className="btn-brand">View History</a>
            : <button className="btn-brand" style={{ minWidth: 180 }} onClick={handleSave} disabled={saving}>
                {saving ? 'Saving…' : 'Save My Diet'}
              </button>
          }
        </div>
      </div>
    </>
  );
}
