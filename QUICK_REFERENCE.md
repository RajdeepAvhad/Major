# EatRight ML Improvements - Quick Reference Card

## 🚀 One-Command Setup

```bash
python scripts/setup_ml_improvements.py
```

---

## 📝 Manual Setup (4 Steps)

```bash
# 1. Install dependencies
pip install imbalanced-learn>=0.12

# 2. Fetch USDA foods (5-10 min)
python scripts/fetch_usda_foods.py

# 3. Merge datasets
python scripts/merge_datasets.py

# 4. Run migrations
python manage.py migrate

# 5. (Optional) Evaluate model
python scripts/evaluate_model.py
```

---

## 📁 Key Files

| File | Purpose | Size |
|------|---------|------|
| `static/data/food_master.csv` | Master dataset (600+ foods) | ~100 KB |
| `static/data/model_insights.json` | Feature importance | ~2 KB |
| `static/data/model_eval.json` | Performance metrics | ~3 KB |
| `static/data/indian_foods.csv` | Indian foods (15 items) | ~1 KB |

---

## 🔧 Key Functions

### `recommender/functions.py`

```python
# New clustering function
apply_clustering(data_array, n_clusters=5)

# New training function with SMOTE
train_with_smote(X_train, y_train, model_name='default')

# Save feature importance
save_feature_importance()
```

---

## 📊 What Changed

| Aspect | Before | After |
|--------|--------|-------|
| **Foods** | 91 | 600+ |
| **Clustering** | K-Means (3) | Agglomerative (5) |
| **Balancing** | None | SMOTE |
| **Features** | Not tracked | Top 5 logged |
| **Evaluation** | None | 5-fold CV |

---

## 🎯 Expected Performance

- **Accuracy**: 80-90%
- **Precision**: 75-85%
- **Recall**: 75-85%
- **F1-Score**: 75-85%

---

## 🔍 Verify Setup

```bash
# Check if master dataset exists
ls static\data\food_master.csv

# Check if migration was created
ls recommender\migrations\0009_add_food_metadata_fields.py

# Check if insights were generated
ls static\data\model_insights.json

# Check if evaluation was run
ls static\data\model_eval.json
```

---

## 🐛 Common Issues

### Issue: USDA API Key Error
```bash
# Check .env file
type .env | findstr USDA_API_KEY
```

### Issue: SMOTE Import Error
```bash
pip install imbalanced-learn
```

### Issue: food_master.csv Not Found
```bash
python scripts/merge_datasets.py
```

---

## 📚 Documentation

- **Complete Guide**: `ML_IMPROVEMENTS_README.md`
- **Summary**: `ML_IMPROVEMENTS_SUMMARY.md`
- **Workflow**: `ML_WORKFLOW.md`
- **This File**: `QUICK_REFERENCE.md`

---

## 🎨 Frontend Integration

### Feature Importance Chart
```javascript
fetch('/static/data/model_insights.json')
  .then(res => res.json())
  .then(data => {
    const features = data.weight_loss.top_features;
    // Render chart
  });
```

### Model Performance Display
```javascript
fetch('/static/data/model_eval.json')
  .then(res => res.json())
  .then(data => {
    const accuracy = data.breakfast.accuracy.mean;
    // Display metrics
  });
```

---

## 🧪 Test Commands

```bash
# Test weight loss recommendations
python manage.py shell
>>> from recommender.functions import Weight_Loss
>>> result = Weight_Loss(age=25, weight=80, height=175)
>>> print(f"Foods: {len(result) - 2}")

# Test weight gain recommendations
>>> from recommender.functions import Weight_Gain
>>> result = Weight_Gain(age=25, weight=55, height=170)
>>> print(f"Foods: {len(result) - 2}")

# Test healthy recommendations
>>> from recommender.functions import Healthy
>>> result = Healthy(age=30, weight=70, height=175)
>>> print(f"Foods: {len(result) - 2}")
```

---

## 📦 New Dependencies

```
imbalanced-learn>=0.12  # For SMOTE oversampling
```

---

## 🗂️ New Model Fields

```python
class Food(models.Model):
    veg = models.BooleanField(default=False)
    glycemic_index = models.FloatField(null=True, blank=True)
    cuisine = models.CharField(max_length=50, default='International')
```

---

## 🎯 Quick Checklist

- [ ] Install `imbalanced-learn`
- [ ] Run `fetch_usda_foods.py`
- [ ] Run `merge_datasets.py`
- [ ] Run `python manage.py migrate`
- [ ] Verify `food_master.csv` exists
- [ ] (Optional) Run `evaluate_model.py`
- [ ] Test recommendations
- [ ] Check `model_insights.json`

---

## 📞 Need Help?

1. Read `ML_IMPROVEMENTS_README.md` for detailed guide
2. Check `ML_IMPROVEMENTS_SUMMARY.md` for overview
3. Review `ML_WORKFLOW.md` for visual diagrams
4. Run automated setup: `python scripts/setup_ml_improvements.py`

---

## 🎉 Success Indicators

✅ `food_master.csv` has 600+ rows  
✅ `model_insights.json` contains feature importance  
✅ `model_eval.json` shows 80%+ accuracy  
✅ Recommendations return diverse food items  
✅ No import errors when running functions  

---

**Last Updated**: 2026-05-26  
**Version**: 1.0  
**Status**: Production Ready ✅
