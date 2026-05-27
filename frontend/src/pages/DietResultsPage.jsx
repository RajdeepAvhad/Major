import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import {
  ArrowDownWideNarrow,
  ArrowLeft,
  ArrowRight,
  BadgeCheck,
  ChefHat,
  ChevronDown,
  Download,
  Filter,
  Flame,
  Heart,
  HeartPulse,
  Leaf,
  Search,
  Save,
  ShoppingCart,
  Sparkles,
  Target,
  UtensilsCrossed,
  Droplets,
  Activity,
  Scale,
} from 'lucide-react';
import FoodCard from '../components/FoodCard';
import ShoppingListModal from '../components/ShoppingListModal';
import ToastContainer, { useToast } from '../utils/Toast';
import { apiGet, apiPost } from '../api/client';
import './DietResultsPage.css';

const CHIP_OPTIONS = [
  'All',
  'Breakfast',
  'Lunch',
  'Dinner',
  'Protein Rich',
  'Low Carb',
  'Weight Loss',
  'Weight Gain',
  'Vegetarian',
  'Vegan',
];

const GI_FILTER_OPTIONS = [
  { value: 'all', label: 'All' },
  { value: 'low', label: 'Low only' },
  { value: 'low-medium', label: 'Low + Medium' },
];

const DEFAULT_WATER_TARGET = 2000;

const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
const toNumber = (value) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
};
const normalizeText = (value) => (value || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();

const resolveImageSrc = (imagepath) => {
  if (!imagepath) return '';
  const trimmed = String(imagepath).trim();
  if (!trimmed) return '';
  if (/^https?:\/\//i.test(trimmed) || trimmed.startsWith('/')) return trimmed;
  return `/static/images/food/${trimmed}`;
};

const estimateCarbs = (food) => {
  if (typeof food?.carbs === 'number') return food.carbs;
  const calories = toNumber(food?.cal);
  const protein = toNumber(food?.pro);
  const fat = toNumber(food?.fat);
  return Math.max(0, (calories - (protein * 4 + fat * 9)) / 4);
};

const getMealLabel = (meal) => {
  if (meal === 'breakfast') return 'Breakfast';
  if (meal === 'lunch') return 'Lunch';
  if (meal === 'dinner') return 'Dinner';
  return 'Meal';
};

const getDietTag = (food) => {
  const calories = toNumber(food.cal);
  const protein = toNumber(food.pro);
  const carbs = estimateCarbs(food);
  const fat = toNumber(food.fat);
  const name = normalizeText(food.name);

  if (/vegan|tofu|pea|bean|lentil|salad|fruit|vegetable|kale|broccoli|spinach|tomato|apple|pear|orange|grape|berry/.test(name)) {
    return 'Vegetarian';
  }
  if (/chicken|fish|egg|tuna|salmon|turkey|beef|pork|shrimp|paneer|yogurt|milk|cheese/.test(name) && protein >= 10) {
    return 'Protein Rich';
  }
  if (protein >= 12) return 'Protein Rich';
  if (carbs <= 20 && calories < 300) return 'Low Carb';
  if (calories < 260) return 'Weight Loss';
  if (calories > 380) return 'Weight Gain';
  if (fat <= 8 && protein >= 6) return 'Low Carb';
  return 'Balanced';
};

const getFoodBadge = (food) => {
  const tag = getDietTag(food);
  if (tag !== 'Balanced') return tag;
  return food.mealLabel || 'Recommended';
};

const getGiCategory = (food) => {
  const value = toNumber(food?.glycemic_index);
  if (!value || value <= 0) return null;
  return food?.gi_category || (value < 55 ? 'Low' : value < 70 ? 'Medium' : 'High');
};

const getFoodPool = (results) => {
  if (!results) return [];
  const meals = [
    { key: 'breakfast', items: results.breakfast || [] },
    { key: 'lunch', items: results.lunch || [] },
    { key: 'dinner', items: results.dinner || [] },
  ];

  const seen = new Map();
  meals.forEach(({ key, items }) => {
    items.forEach((food, index) => {
      const stableKey = food.id ?? `${food.name}-${key}-${index}`;
      const enriched = {
        ...food,
        id: food.id ?? stableKey,
        meal: key,
        mealLabel: getMealLabel(key),
        carbs: estimateCarbs(food),
        dietTag: getDietTag(food),
        giCategory: getGiCategory(food),
        imageSrc: resolveImageSrc(food.imagepath),
      };
      const existing = seen.get(stableKey);
      if (existing) {
        existing.availableMeals = Array.from(new Set([...(existing.availableMeals || []), key]));
        existing.mealLabel = existing.availableMeals.length > 1 ? 'Any meal' : existing.mealLabel;
        seen.set(stableKey, existing);
      } else {
        seen.set(stableKey, { ...enriched, availableMeals: [key] });
      }
    });
  });

  return Array.from(seen.values()).map(food => ({
    ...food,
    badge: getFoodBadge(food),
    searchText: normalizeText([food.name, food.mealLabel, food.dietTag].join(' ')),
  }));
};

const getBMIStatus = (bmi) => {
  if (!bmi) return 'Not available';
  if (bmi < 18.5) return 'Underweight';
  if (bmi < 25) return 'Healthy';
  if (bmi < 30) return 'Overweight';
  return 'Obese';
};

const getBMIProgress = (bmi) => clamp((toNumber(bmi) / 40) * 100, 0, 100);
const getPlanDays = (planPeriod, planDate) => {
  if (planPeriod === 'weekly') return 7;
  if (planPeriod === 'monthly') {
    const date = new Date(planDate);
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  }
  return 1;
};

const SectionShell = ({ title, subtitle, children, action }) => (
  <motion.section
    className="diet-panel"
    initial={{ opacity: 0, y: 16 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true, amount: 0.18 }}
    transition={{ duration: 0.3 }}
  >
    <div className="diet-panel__header">
      <div>
        <h2>{title}</h2>
        {subtitle && <p>{subtitle}</p>}
      </div>
      {action}
    </div>
    {children}
  </motion.section>
);

const CircleStat = ({ current, target, label, unit, icon: Icon, accent = '#22C55E', subtext, size = 70 }) => {
  const percent = target ? clamp((current / target) * 100, 0, 100) : 0;
  const radius = 28;
  const circumference = 2 * Math.PI * radius;
  const dash = circumference - (percent / 100) * circumference;

  return (
    <div className="diet-stat-card">
      <div className="diet-stat-card__top">
        <span className="diet-stat-card__icon" style={{ color: accent }}><Icon size={16} /></span>
        <span className="diet-stat-card__label">{label}</span>
      </div>
      <div className="diet-stat-card__body">
        <svg viewBox="0 0 72 72" width={size} height={size} className="diet-stat-ring">
          <circle cx="36" cy="36" r={radius} className="diet-stat-ring__track" />
          <circle
            cx="36"
            cy="36"
            r={radius}
            className="diet-stat-ring__progress"
            style={{ stroke: accent, strokeDasharray: circumference, strokeDashoffset: dash }}
          />
        </svg>
        <div className="diet-stat-card__values">
          <strong>{Math.round(current)}</strong>
          <span>{Math.round(target)} {unit}</span>
          {subtext && <small>{subtext}</small>}
        </div>
      </div>
    </div>
  );
};

export default function DietResultsPage() {
  const navigate = useNavigate();
  const { toasts, addToast, removeToast } = useToast();
  const [results, setResults] = useState(null);
  const [selected, setSelected] = useState({});
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  const [favorites, setFavorites] = useState([]);
  const [shoppingListData, setShoppingListData] = useState(null);
  const [showShoppingList, setShowShoppingList] = useState(false);
  const [selectedMacros, setSelectedMacros] = useState({ cal: 0, pro: 0, fat: 0, carbs: 0 });
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [giFilter, setGiFilter] = useState('all');
  const [sortBy, setSortBy] = useState('recommended');
  const [insightsOpen, setInsightsOpen] = useState(false);
  const [waterToday, setWaterToday] = useState({ amount_ml: 0 });
  const favoritesRef = useRef(null);

  useEffect(() => {
    const stored = sessionStorage.getItem('dietResults');
    if (stored) setResults(JSON.parse(stored));
    else navigate('/dietplanner');
  }, [navigate]);

  useEffect(() => {
    apiGet('/api/favorites/')
      .then(res => {
        if (res.ok) {
          const normalized = (res.favorites || []).map(f => ({ ...f, id: f.food_id || f.id }));
          setFavorites(normalized);
        }
      })
      .catch(() => {});

    apiGet('/api/water/')
      .then(res => {
        if (res.ok && res.today) setWaterToday(res.today);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    const foods = Object.values(selected);
    let cal = 0;
    let pro = 0;
    let fat = 0;
    let carbs = 0;

    foods.forEach(food => {
      cal += toNumber(food.cal);
      pro += toNumber(food.pro);
      fat += toNumber(food.fat);
      carbs += estimateCarbs(food);
    });

    setSelectedMacros({ cal, pro, fat, carbs });
  }, [selected]);

  if (!results) {
    return (
      <div className="diet-results-page diet-results-page--loading">
        <div className="diet-skeleton diet-skeleton--summary" />
        <div className="diet-skeleton-grid">
          <div className="diet-skeleton diet-skeleton--card" />
          <div className="diet-skeleton diet-skeleton--card" />
          <div className="diet-skeleton diet-skeleton--card" />
          <div className="diet-skeleton diet-skeleton--card" />
        </div>
      </div>
    );
  }

  const targetCal = toNumber(results.caloriesreq);
  const planPeriod = results.plan_period || 'daily';
  const planDate = results.plan_date || new Date().toISOString().slice(0, 10);
  const totalCal = Object.values(selected).reduce((sum, food) => sum + toNumber(food.cal), 0);
  const remainingCal = Math.max(0, targetCal - totalCal);
  const progressPercent = targetCal ? clamp((totalCal / targetCal) * 100, 0, 100) : 0;
  const planDays = getPlanDays(planPeriod, planDate);
  const favoriteIds = new Set(favorites.map(food => food.id));
  const recommendedFoods = getFoodPool(results);
  const selectedMeals = new Set(Object.values(selected).map(food => `${food.meal}-${food.id}`));

  const handleToggleFavorite = async (food) => {
    const res = await apiPost('/api/favorites/toggle/', { food_id: food.id });
    if (!res.ok) return;
    setFavorites(prev => {
      const exists = prev.find(item => item.id === food.id);
      if (exists) return prev.filter(item => item.id !== food.id);
      return [{ ...food, id: food.id }, ...prev];
    });
  };

  const toggle = (food, meal = food.meal) => {
    const key = `${meal}-${food.id}`;
    setSelected(prev => {
      const copy = { ...prev };
      if (copy[key]) {
        delete copy[key];
        addToast(`Removed ${food.name}`, 'info', 1800);
      } else {
        copy[key] = food;
        addToast(`Added ${food.name}`, 'success', 1800);
      }
      return copy;
    });
  };

  const handleSave = async () => {
    const items = Object.entries(selected).map(([key, food]) => ({
      name: food.name,
      meal: key.split('-')[0],
      calories: food.cal,
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
    if (selectedFoods.length === 0) {
      addToast('Select some foods first to export your plan.', 'warning');
      return;
    }

    const byMeal = {};
    selectedFoods.forEach(([key, food]) => {
      const meal = key.split('-')[0];
      if (!byMeal[meal]) byMeal[meal] = [];
      byMeal[meal].push(food);
    });

    const mealHtml = Object.entries(byMeal).map(([meal, foods]) => `
      <h3 style="color:#22C55E;text-transform:capitalize;margin-top:20px">${meal}</h3>
      <table style="width:100%;border-collapse:collapse;font-size:14px">
        <thead>
          <tr style="background:#22C55E;color:#0F1117">
            <th style="padding:6px 10px;text-align:left">Food</th>
            <th style="padding:6px 10px;text-align:right">Calories</th>
            <th style="padding:6px 10px;text-align:right">Protein</th>
            <th style="padding:6px 10px;text-align:right">Fat</th>
            <th style="padding:6px 10px;text-align:right">Carbs</th>
          </tr>
        </thead>
        <tbody>
          ${foods.map((food, index) => `
            <tr style="background:${index % 2 === 0 ? '#171A21' : '#202531'}">
              <td style="padding:6px 10px">${food.name}</td>
              <td style="padding:6px 10px;text-align:right">${toNumber(food.cal)}</td>
              <td style="padding:6px 10px;text-align:right">${toNumber(food.pro)}</td>
              <td style="padding:6px 10px;text-align:right">${toNumber(food.fat)}</td>
              <td style="padding:6px 10px;text-align:right">${Math.round(estimateCarbs(food))}</td>
            </tr>`).join('')}
        </tbody>
      </table>`).join('');

    const win = window.open('', '_blank');
    if (!win) return;

    win.document.write(`<!DOCTYPE html><html><head>
      <title>My EatRight Diet Plan</title>
      <style>
        body{font-family:Inter,Arial,sans-serif;background:#0F1117;color:#E2E8F0;padding:30px;max-width:900px;margin:0 auto}
        h1,h2{color:#22C55E}th,td{border-bottom:1px solid rgba(255,255,255,.08)}
      </style>
    </head><body>
      <h1>My EatRight Diet Plan</h1>
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

    const shoppingList = [
      {
        category: 'All Items',
        items: selectedFoods.map(food => ({
          name: food.name,
          quantity: 1,
          unit: 'serving',
          notes: `${toNumber(food.cal)} kcal`,
        })),
      },
    ];

    setShoppingListData(shoppingList);
    setShowShoppingList(true);
    addToast('Shopping list generated!', 'success');
  };

  const filteredFoods = recommendedFoods
    .filter(food => {
      const matchesSearch = !searchTerm.trim() || food.searchText.includes(normalizeText(searchTerm));
      const matchesCategory = categoryFilter === 'All' || food.mealLabel === categoryFilter || food.dietTag === categoryFilter;
      const matchesGi = giFilter === 'all'
        || (giFilter === 'low' && food.giCategory === 'Low')
        || (giFilter === 'low-medium' && ['Low', 'Medium'].includes(food.giCategory));
      return matchesSearch && matchesCategory && matchesGi;
    })
    .sort((a, b) => {
      if (sortBy === 'calories') return toNumber(a.cal) - toNumber(b.cal);
      if (sortBy === 'protein') return toNumber(b.pro) - toNumber(a.pro);
      return 0;
    });

  const selectedGiCounts = Object.values(selected).reduce((counts, food) => {
    const category = getGiCategory(food);
    if (category === 'Low') counts.low += 1;
    else if (category === 'Medium') counts.medium += 1;
    else if (category === 'High') counts.high += 1;
    return counts;
  }, { low: 0, medium: 0, high: 0 });

  const bmiStatus = getBMIStatus(results.bmi);
  const bmiProgress = getBMIProgress(results.bmi);
  const bodyFat = toNumber(results.bodyfat);
  const waterCurrent = toNumber(waterToday?.amount_ml);

  const handleArrowScroll = (direction) => {
    favoritesRef.current?.scrollBy({ left: direction * 420, behavior: 'smooth' });
  };

  return (
    <>
      <ToastContainer toasts={toasts} removeToast={removeToast} />
      <ShoppingListModal
        isOpen={showShoppingList}
        onClose={() => setShowShoppingList(false)}
        shoppingList={shoppingListData}
      />

      <div className="diet-results-page">
        <motion.div
          className="diet-summary-bar"
          initial={{ opacity: 0, y: -16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <div className="diet-summary-bar__left">
            <div className="diet-summary-bar__eyebrow">
              <Sparkles size={14} /> Daily goal
            </div>
            <div className="diet-summary-bar__numbers">
              <div>
                <strong>{Math.round(totalCal)} / {Math.round(targetCal)} kcal</strong>
                <span>{remainingCal} kcal remaining</span>
              </div>
              <p>{planPeriod} plan · {planDate}</p>
            </div>
          </div>

          <div className="diet-summary-bar__center">
            <div className="diet-progress-ring">
              <svg viewBox="0 0 72 72">
                <circle cx="36" cy="36" r="28" className="diet-progress-ring__track" />
                <motion.circle
                  cx="36"
                  cy="36"
                  r="28"
                  className="diet-progress-ring__progress"
                  initial={{ strokeDashoffset: 175.9 }}
                  animate={{ strokeDashoffset: 175.9 - (progressPercent / 100) * 175.9 }}
                  transition={{ duration: 0.7, ease: 'easeOut' }}
                  style={{ strokeDasharray: 175.9 }}
                />
              </svg>
              <div className="diet-progress-ring__text">
                <strong>{Math.round(progressPercent)}%</strong>
                <span>Goal</span>
              </div>
            </div>
            <div className="diet-summary-pill">
              <Target size={15} />
              <span>{Math.round(remainingCal)} kcal remaining</span>
            </div>
          </div>

          <div className="diet-summary-bar__actions">
            <button className="diet-action-button diet-action-button--teal" onClick={handlePrint}>
              <Download size={16} /> Export Plan
            </button>
            <button className="diet-action-button diet-action-button--violet" onClick={handleShoppingList}>
              <ShoppingCart size={16} /> Shopping List
            </button>
            {saved ? (
              <span className="diet-save-status"><BadgeCheck size={16} /> Saved</span>
            ) : (
              <button className="diet-action-button diet-action-button--primary" onClick={handleSave} disabled={saving}>
                <Save size={16} /> {saving ? 'Saving…' : 'Save Diet'}
              </button>
            )}
          </div>
        </motion.div>

        <main className="diet-results-main">
          <SectionShell
            title="Recommended Foods For You"
            subtitle="Select foods to build today’s meal plan"
            action={<span className="diet-section-kicker"><ChefHat size={15} /> Plan first, insights second</span>}
          >
            <div className="diet-controls">
              <label className="diet-control">
                <Search size={16} />
                <input
                  type="text"
                  placeholder="Search food"
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                />
              </label>

              <label className="diet-control diet-control--select">
                <Filter size={16} />
                <select value={categoryFilter} onChange={e => setCategoryFilter(e.target.value)}>
                  {CHIP_OPTIONS.map(option => <option key={option} value={option}>{option}</option>)}
                </select>
              </label>

              <label className="diet-control diet-control--select">
                <Leaf size={16} />
                <select value={giFilter} onChange={e => setGiFilter(e.target.value)}>
                  {GI_FILTER_OPTIONS.map(option => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </label>

              <div className="diet-sort-group">
                <button
                  className={`diet-sort-button ${sortBy === 'calories' ? 'is-active' : ''}`}
                  onClick={() => setSortBy(sortBy === 'calories' ? 'recommended' : 'calories')}
                >
                  <ArrowDownWideNarrow size={15} /> Calories
                </button>
                <button
                  className={`diet-sort-button ${sortBy === 'protein' ? 'is-active' : ''}`}
                  onClick={() => setSortBy(sortBy === 'protein' ? 'recommended' : 'protein')}
                >
                  <ArrowDownWideNarrow size={15} /> Protein
                </button>
              </div>
            </div>

            <div className="diet-chip-row">
              {CHIP_OPTIONS.map(option => (
                <button
                  key={option}
                  className={`diet-chip ${categoryFilter === option ? 'is-selected' : ''}`}
                  onClick={() => setCategoryFilter(option)}
                >
                  {option}
                </button>
              ))}
            </div>

            <div className="diet-card-grid">
              <AnimatePresence mode="popLayout">
                {filteredFoods.map((food, index) => (
                  <motion.div
                    key={`${food.id}-${food.meal}`}
                    layout
                    initial={{ opacity: 0, y: 18, scale: 0.98 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 12, scale: 0.96 }}
                    transition={{ duration: 0.3, delay: Math.min(index * 0.015, 0.2) }}
                  >
                    <FoodCard
                      food={food}
                      meal={food.meal}
                      checked={selectedMeals.has(`${food.meal}-${food.id}`)}
                      onToggle={toggle}
                      isFavorite={favoriteIds.has(food.id)}
                      onToggleFavorite={handleToggleFavorite}
                    />
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </SectionShell>

          <section className="diet-gi-summary">
            <div>
              <h3>Glycemic Index Summary</h3>
              <p>Your meal plan: {selectedGiCounts.low} Low GI, {selectedGiCounts.medium} Medium GI, {selectedGiCounts.high} High GI foods</p>
            </div>
            {String(results.goal || '').toLowerCase() === 'weight loss' && (
              <div className="diet-gi-summary__tip">
                Prefer Low GI foods to manage blood sugar and hunger
              </div>
            )}
          </section>

          <motion.section
            className="diet-panel"
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.18 }}
            transition={{ duration: 0.3 }}
          >
            <button className="diet-accordion" onClick={() => setInsightsOpen(open => !open)}>
              <div>
                <h2>Health Insights</h2>
                <p>BMI, body fat, and daily calorie requirement</p>
              </div>
              <ChevronDown className={`diet-accordion__chevron ${insightsOpen ? 'is-open' : ''}`} size={18} />
            </button>

            <AnimatePresence initial={false}>
              {insightsOpen && (
                <motion.div
                  className="diet-insights-grid"
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="diet-health-card diet-health-card--radial">
                    <div className="diet-health-card__title">
                      <Scale size={16} /> BMI
                    </div>
                    <div className="diet-radial">
                      <svg viewBox="0 0 72 72">
                        <circle cx="36" cy="36" r="28" className="diet-progress-ring__track" />
                        <circle
                          cx="36"
                          cy="36"
                          r="28"
                          className="diet-progress-ring__progress"
                          style={{ strokeDasharray: 175.9, strokeDashoffset: 175.9 - (bmiProgress / 100) * 175.9 }}
                        />
                      </svg>
                      <div className="diet-radial__text">
                        <strong>{toNumber(results.bmi).toFixed(1)}</strong>
                        <span>{bmiStatus}</span>
                      </div>
                    </div>
                    <p>{results.bmiinfo}</p>
                  </div>

                  <div className="diet-health-card">
                    <div className="diet-health-card__title">
                      <HeartPulse size={16} /> Body Fat
                    </div>
                    <div className="diet-health-card__metric">
                      <strong>{bodyFat ? `${bodyFat.toFixed(1)}%` : '—'}</strong>
                      <span>{results.bodyfat_source === 'calculated' ? 'Auto-calculated' : 'From your profile'}</span>
                    </div>
                    <p>Body fat is used to refine calorie and macro recommendations.</p>
                  </div>

                  <div className="diet-health-card">
                    <div className="diet-health-card__title">
                      <Activity size={16} /> Daily Calorie Requirement
                    </div>
                    <div className="diet-health-card__metric">
                      <strong>{Math.round(targetCal)} kcal</strong>
                      <span>{planPeriod} plan · {planDays} day horizon</span>
                    </div>
                    <p>Recommended intake based on your selected goal and profile.</p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.section>

          <SectionShell
            title="Nutrition Dashboard"
            subtitle="Daily targets with compact progress indicators"
            action={<span className="diet-section-kicker"><Flame size={15} /> macro balance</span>}
          >
            <div className="diet-nutrition-grid">
              <CircleStat current={selectedMacros.cal} target={targetCal || 1} label="Calories" unit="kcal" icon={Flame} accent="#22C55E" subtext="Consumed" />
              <CircleStat current={selectedMacros.pro} target={Math.max(50, targetCal / 10)} label="Protein" unit="g" icon={Leaf} accent="#38BDF8" subtext="Lean support" />
              <CircleStat current={selectedMacros.carbs} target={Math.max(300, (targetCal * 0.5) / 4)} label="Carbs" unit="g" icon={UtensilsCrossed} accent="#A78BFA" subtext="Energy" />
              <CircleStat current={selectedMacros.fat} target={Math.max(65, targetCal / 30)} label="Fat" unit="g" icon={Target} accent="#F59E0B" subtext="Balance" />
              <CircleStat current={waterCurrent} target={DEFAULT_WATER_TARGET} label="Water Intake" unit="ml" icon={Droplets} accent="#60A5FA" subtext="Hydration" />
            </div>
          </SectionShell>

          <SectionShell
            title="Favorite Foods"
            subtitle="Quickly revisit meals you already love"
          >
            {favorites.length === 0 ? (
              <div className="diet-empty-state">
                <div className="diet-empty-state__illustration">
                  <Heart size={34} />
                </div>
                <h3>No favorites yet</h3>
                <p>Tap the heart on any food card to add it to this carousel.</p>
              </div>
            ) : (
              <div className="diet-favorites-shell">
                <button className="diet-carousel-nav" onClick={() => handleArrowScroll(-1)} aria-label="Scroll favorites left">
                  <ArrowLeft size={16} />
                </button>

                <div className="diet-favorites-track" ref={favoritesRef}>
                  {favorites.map(food => (
                    <div className="diet-favorite-card" key={food.id}>
                      <FoodCard
                        food={{
                          ...food,
                          meal: 'breakfast',
                          mealLabel: 'Favorite',
                          badge: getFoodBadge(food),
                          carbs: estimateCarbs(food),
                          imageSrc: resolveImageSrc(food.imagepath),
                        }}
                        meal="breakfast"
                        checked={selectedMeals.has(`breakfast-${food.id}`)}
                        onToggle={toggle}
                        isFavorite={true}
                        onToggleFavorite={handleToggleFavorite}
                      />
                    </div>
                  ))}
                </div>

                <button className="diet-carousel-nav" onClick={() => handleArrowScroll(1)} aria-label="Scroll favorites right">
                  <ArrowRight size={16} />
                </button>
              </div>
            )}
          </SectionShell>

          <div className="diet-footer-actions">
            {saved ? (
              <a href="/diet-history" className="diet-action-button diet-action-button--ghost">View History</a>
            ) : (
              <button className="diet-action-button diet-action-button--primary" onClick={handleSave} disabled={saving}>
                <Save size={16} /> {saving ? 'Saving…' : 'Save My Diet'}
              </button>
            )}
          </div>
        </main>
      </div>
    </>
  );
}
