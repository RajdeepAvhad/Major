export default function FoodCard({ food, meal, checked, onToggle, isFavorite, onToggleFavorite }) {
  const imgSrc = food.imagepath
    ? `/static/images/food/${food.imagepath}`
    : '/static/images/Gemini_Generated_Image_f0bd5kf0bd5kf0bd.png';

  return (
    <div className="food-card">
      {onToggleFavorite && (
        <button
          className="fav-btn"
          type="button"
          onClick={() => onToggleFavorite(food)}
        >
          {isFavorite ? 'Unfav' : 'Fav'}
        </button>
      )}
      <img src={imgSrc} alt={food.name} onError={e => { e.target.src = '/static/images/Gemini_Generated_Image_f0bd5kf0bd5kf0bd.png'; }} />
      <div className="food-card-body">
        <div className="food-card-title">{food.name}</div>
        <div style={{ fontSize: 12, color: '#aaa' }}>
          <div>Cal: <strong>{food.cal}</strong></div>
          <div>Fat: {food.fat}g | Pro: {food.pro}g | Sug: {food.sug}g</div>
        </div>
        <label style={{ marginTop: 6, display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={checked}
            onChange={() => onToggle(food, meal)}
            style={{ accentColor: '#2ECC71' }}
          />
          <span style={{ fontSize: 12, fontWeight: 500, color: '#2ECC71' }}>Add This</span>
        </label>
      </div>
    </div>
  );
}
