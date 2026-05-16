import React, { useState } from 'react';
import FoodCard from './FoodCard';
import './FavoriteFoodsPanel.css';

const FavoriteFoodsPanel = ({ favorites = [], onAddToMeal }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!favorites || favorites.length === 0) {
    return (
      <div className="favorites-panel favorites-empty">
        <div className="favorites-header">
          <button
            className="favorites-toggle"
            onClick={() => setIsExpanded(!isExpanded)}
            aria-expanded={isExpanded}
          >
            <span className="favorites-title">❤️ Your Favorites ({favorites.length})</span>
            <span className={`favorites-arrow ${isExpanded ? 'open' : ''}`}>▼</span>
          </button>
        </div>
        {isExpanded && (
          <div className="favorites-empty-message">
            <p>No favorites yet. Mark foods as favorites to save them here!</p>
            <p className="favorites-hint">💡 Tip: Click the heart icon on any food to add it to your favorites</p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="favorites-panel">
      <div className="favorites-header">
        <button
          className="favorites-toggle"
          onClick={() => setIsExpanded(!isExpanded)}
          aria-expanded={isExpanded}
        >
          <span className="favorites-title">❤️ Your Favorites ({favorites.length})</span>
          <span className={`favorites-arrow ${isExpanded ? 'open' : ''}`}>▼</span>
        </button>
      </div>

      {isExpanded && (
        <div className="favorites-grid">
          {favorites.map((food) => (
            <div key={food.id} className="favorite-food-wrapper">
              <FoodCard food={food} onFavoriteToggle={() => {}} isFavorite={true} />
              {onAddToMeal && (
                <div className="favorite-meal-buttons">
                  <button
                    className="btn-add-meal breakfast-btn"
                    onClick={() => onAddToMeal('breakfast', food)}
                    title="Add to Breakfast"
                  >
                    🌅
                  </button>
                  <button
                    className="btn-add-meal lunch-btn"
                    onClick={() => onAddToMeal('lunch', food)}
                    title="Add to Lunch"
                  >
                    🌤️
                  </button>
                  <button
                    className="btn-add-meal dinner-btn"
                    onClick={() => onAddToMeal('dinner', food)}
                    title="Add to Dinner"
                  >
                    🌙
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FavoriteFoodsPanel;
