import { useState } from 'react';
import { Heart, Plus, Sparkles, Flame, Beef, Wheat, Droplets } from 'lucide-react';
import './FoodCard.css';

const resolveImageSrc = (imagepath) => {
  if (!imagepath) return '';
  const trimmed = String(imagepath).trim();
  if (!trimmed) return '';
  if (/^https?:\/\//i.test(trimmed) || trimmed.startsWith('/')) return trimmed;
  return `/static/images/food/${trimmed}`;
};

const normalizeName = (value) => (value || '').toLowerCase();

const getGiMeta = (food) => {
  const giValue = Number(food.glycemic_index);
  if (!Number.isFinite(giValue) || giValue <= 0) return null;

  const category = food.gi_category || (giValue < 55 ? 'Low' : giValue < 70 ? 'Medium' : 'High');
  if (category === 'Low') return { label: 'Low GI', tone: 'gi-low' };
  if (category === 'Medium') return { label: 'Medium GI', tone: 'gi-medium' };
  if (category === 'High') return { label: 'High GI', tone: 'gi-high' };
  return null;
};

const getCategoryMeta = (food) => {
  const name = normalizeName(food.name);
  const badge = food.badge || food.dietTag || food.mealLabel || 'Recommended';

  if (/chicken|beef|pork|turkey|fish|tuna|salmon|egg|paneer|yogurt|milk|cheese/.test(name)) {
    return { icon: Beef, tone: 'protein', badge };
  }
  if (/rice|bread|oat|wheat|pasta|roti|idli|dosa|poha|upma|quinoa/.test(name)) {
    return { icon: Wheat, tone: 'grain', badge };
  }
  if (/water|juice|milk|yogurt/.test(name)) {
    return { icon: Droplets, tone: 'fresh', badge };
  }
  return { icon: Sparkles, tone: 'fresh', badge };
};

export default function FoodCard({ food, meal, checked, onToggle, isFavorite, onToggleFavorite }) {
  const [imageError, setImageError] = useState(false);
  const imageSrc = resolveImageSrc(food.imageSrc || food.imagepath);
  const showImage = Boolean(imageSrc) && !imageError;
  const carbs = typeof food.carbs === 'number' ? food.carbs : Math.max(0, (Number(food.cal || 0) - (Number(food.pro || 0) * 4 + Number(food.fat || 0) * 9)) / 4);
  const meta = getCategoryMeta(food);
  const giMeta = getGiMeta(food);
  const Icon = meta.icon;

  return (
    <article className="food-card-glass">
      <div className="food-card-glass__media">
        {showImage ? (
          <img
            src={imageSrc}
            alt={food.name}
            loading="lazy"
            onError={() => setImageError(true)}
          />
        ) : (
          <div className="food-card-glass__placeholder">
            <Icon size={30} />
          </div>
        )}

        <div className="food-card-glass__overlay">
          <span className={`food-card-glass__badge food-card-glass__badge--${meta.tone}`}>
            {meta.badge}
          </span>
          <span className="food-card-glass__meal-badge">
            {food.mealLabel || meal || 'Meal'}
          </span>
        </div>

        {onToggleFavorite && (
          <button
            className={`food-card-glass__favorite ${isFavorite ? 'is-active' : ''}`}
            type="button"
            onClick={() => onToggleFavorite(food)}
            aria-label={isFavorite ? 'Remove favorite' : 'Add favorite'}
          >
            <Heart size={15} fill={isFavorite ? 'currentColor' : 'none'} />
          </button>
        )}
      </div>

      <div className="food-card-glass__body">
        <h3>{food.name}</h3>

        {giMeta && (
          <span className={`food-card-glass__gi-badge food-card-glass__gi-badge--${giMeta.tone}`}>
            {giMeta.label}
          </span>
        )}

        <div className="food-card-glass__stats">
          <span><Flame size={13} /> {Math.round(Number(food.cal || 0))} kcal</span>
          <span><Beef size={13} /> {Math.round(Number(food.pro || 0))}g</span>
          <span><Wheat size={13} /> {Math.round(carbs)}g</span>
          <span><Droplets size={13} /> {Math.round(Number(food.fat || 0))}g</span>
        </div>

        <div className="food-card-glass__actions">
          <button
            className={`food-card-glass__plan-btn ${checked ? 'is-selected' : ''}`}
            type="button"
            onClick={() => onToggle(food, meal)}
          >
            {checked ? <><Sparkles size={14} /> Added</> : <><Plus size={14} /> Add To Plan</>}
          </button>

          <button
            className={`food-card-glass__like-btn ${isFavorite ? 'is-active' : ''}`}
            type="button"
            onClick={() => onToggleFavorite?.(food)}
            aria-label={isFavorite ? 'Unfavorite' : 'Favorite'}
          >
            <Heart size={15} fill={isFavorite ? 'currentColor' : 'none'} />
          </button>
        </div>
      </div>
    </article>
  );
}
