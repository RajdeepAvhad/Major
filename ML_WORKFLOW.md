# EatRight ML Workflow - Visual Guide

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                                 │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
            ┌──────────┐  ┌──────────┐  ┌──────────┐
            │ food.csv │  │   USDA   │  │  Indian  │
            │ (91 items)│  │   API    │  │  Foods   │
            └──────────┘  │(500+ items)│ │(15 items)│
                          └──────────┘  └──────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  scripts/               │
                    │  fetch_usda_foods.py    │
                    │  ├─ Fetch from API      │
                    │  ├─ Map nutrients       │
                    │  └─ Save to CSV         │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │ food_expanded.csv       │
                    │ (500+ USDA foods)       │
                    └─────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
            ┌──────────┐  ┌──────────┐  ┌──────────┐
            │ food.csv │  │ expanded │  │  indian  │
            └──────────┘  └──────────┘  └──────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  scripts/               │
                    │  merge_datasets.py      │
                    │  ├─ Merge all CSVs      │
                    │  ├─ Deduplicate         │
                    │  ├─ Normalize           │
                    │  └─ Save master         │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │ food_master.csv         │
                    │ (600+ unique foods)     │
                    └─────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      ML TRAINING PIPELINE                            │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
            ┌──────────┐  ┌──────────┐  ┌──────────┐
            │Breakfast │  │  Lunch   │  │  Dinner  │
            │  Foods   │  │  Foods   │  │  Foods   │
            └──────────┘  └──────────┘  └──────────┘
                    │             │             │
                    ▼             ▼             ▼
            ┌──────────────────────────────────────┐
            │  Agglomerative Clustering            │
            │  ├─ n_clusters = 5                   │
            │  ├─ linkage = 'ward'                 │
            │  └─ Better food grouping             │
            └──────────────────────────────────────┘
                                  │
                                  ▼
            ┌──────────────────────────────────────┐
            │  Create Training Data                │
            │  ├─ Combine with BMI classes         │
            │  ├─ Combine with Age classes         │
            │  └─ Generate synthetic samples       │
            └──────────────────────────────────────┘
                                  │
                                  ▼
            ┌──────────────────────────────────────┐
            │  SMOTE Oversampling                  │
            │  ├─ Balance minority classes         │
            │  ├─ k_neighbors = 5                  │
            │  └─ Synthetic sample generation      │
            └──────────────────────────────────────┘
                                  │
                                  ▼
            ┌──────────────────────────────────────┐
            │  Random Forest Training              │
            │  ├─ n_estimators = 100               │
            │  ├─ random_state = 42                │
            │  └─ Track feature importance         │
            └──────────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
            ┌──────────┐  ┌──────────┐  ┌──────────┐
            │Weight Loss│ │Weight Gain│ │ Healthy  │
            │  Model    │ │  Model    │ │  Model   │
            └──────────┘  └──────────┘  └──────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         MODEL OUTPUTS                                │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │ Predictions  │  │   Feature    │  │  Evaluation  │
        │ (Food Items) │  │  Importance  │  │   Metrics    │
        └──────────────┘  └──────────────┘  └──────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  model_insights.json    │
                    │  ├─ Top 5 features      │
                    │  └─ Per model type      │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  model_eval.json        │
                    │  ├─ Accuracy            │
                    │  ├─ Precision           │
                    │  ├─ Recall              │
                    │  └─ F1-Score            │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │   Frontend Dashboard    │
                    │   (Future Integration)  │
                    └─────────────────────────┘
```

---

## 🔄 Recommendation Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INPUT                                   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
            ┌──────────┐  ┌──────────┐  ┌──────────┐
            │   Age    │  │  Weight  │  │  Height  │
            └──────────┘  └──────────┘  └──────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Calculate BMI          │
                    │  BMI = weight/(height²) │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Classify BMI           │
                    │  ├─ Underweight (< 18.5)│
                    │  ├─ Healthy (18.5-25)   │
                    │  ├─ Overweight (25-30)  │
                    │  └─ Obese (> 30)        │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Classify Age           │
                    │  ├─ 0-20 years          │
                    │  ├─ 20-40 years         │
                    │  ├─ 40-60 years         │
                    │  └─ 60+ years           │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Select Goal            │
                    │  ├─ Weight Loss         │
                    │  ├─ Weight Gain         │
                    │  └─ Healthy Maintenance │
                    └─────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │ Weight_Loss()│  │ Weight_Gain()│  │  Healthy()   │
        └──────────────┘  └──────────────┘  └──────────────┘
                                  │
                                  ▼
            ┌──────────────────────────────────────┐
            │  Load food_master.csv                │
            │  (600+ foods)                        │
            └──────────────────────────────────────┘
                                  │
                                  ▼
            ┌──────────────────────────────────────┐
            │  Filter by Meal Type                 │
            │  ├─ Breakfast foods                  │
            │  ├─ Lunch foods                      │
            │  └─ Dinner foods                     │
            └──────────────────────────────────────┘
                                  │
                                  ▼
            ┌──────────────────────────────────────┐
            │  Apply Agglomerative Clustering      │
            │  (5 clusters per meal type)          │
            └──────────────────────────────────────┘
                                  │
                                  ▼
            ┌──────────────────────────────────────┐
            │  Prepare Test Data                   │
            │  ├─ User's BMI class                 │
            │  ├─ User's Age class                 │
            │  └─ Nutrition distribution           │
            └──────────────────────────────────────┘
                                  │
                                  ▼
            ┌──────────────────────────────────────┐
            │  Train Random Forest with SMOTE      │
            │  ├─ Balance classes                  │
            │  ├─ Fit model                        │
            │  └─ Track feature importance         │
            └──────────────────────────────────────┘
                                  │
                                  ▼
            ┌──────────────────────────────────────┐
            │  Predict Food Clusters               │
            │  (Which cluster matches user?)       │
            └──────────────────────────────────────┘
                                  │
                                  ▼
            ┌──────────────────────────────────────┐
            │  Filter Recommended Foods            │
            │  (Foods in predicted cluster)        │
            └──────────────────────────────────────┘
                                  │
                                  ▼
            ┌──────────────────────────────────────┐
            │  Save Feature Importance             │
            │  (model_insights.json)               │
            └──────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    RETURN RECOMMENDATIONS                            │
│  ├─ List of recommended food items                                  │
│  ├─ User's BMI value                                                │
│  └─ BMI interpretation message                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Algorithm Comparison

### Before: K-Means Clustering

```
┌─────────────────────────────────────────┐
│         K-Means (3 Clusters)            │
├─────────────────────────────────────────┤
│  Cluster 0: Low Calorie Foods           │
│  Cluster 1: Medium Calorie Foods        │
│  Cluster 2: High Calorie Foods          │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Limitations:                           │
│  ├─ Only 3 broad categories             │
│  ├─ No hierarchical structure           │
│  ├─ Less diverse recommendations        │
│  └─ May miss nuanced food groups        │
└─────────────────────────────────────────┘
```

### After: Agglomerative Clustering

```
┌─────────────────────────────────────────┐
│  Agglomerative (5 Clusters, Ward)      │
├─────────────────────────────────────────┤
│  Cluster 0: Very Low Calorie            │
│  Cluster 1: Low Calorie, High Fiber     │
│  Cluster 2: Moderate Calorie, Balanced  │
│  Cluster 3: High Protein                │
│  Cluster 4: High Calorie, High Fat      │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Benefits:                              │
│  ├─ 5 granular categories               │
│  ├─ Hierarchical food grouping          │
│  ├─ More diverse recommendations        │
│  └─ Better captures food similarities   │
└─────────────────────────────────────────┘
```

---

## 🔬 SMOTE Oversampling Process

```
┌─────────────────────────────────────────────────────────────────────┐
│                    BEFORE SMOTE                                      │
└─────────────────────────────────────────────────────────────────────┘

Training Data Distribution:
Cluster 0: ████████████████████ (100 samples)
Cluster 1: ██████████ (50 samples)
Cluster 2: ████████████████████████████ (140 samples)
Cluster 3: ████ (20 samples)  ← Minority class
Cluster 4: ████████ (40 samples)

Problem: Model biased towards Cluster 2, ignores Cluster 3

                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SMOTE PROCESS                                     │
└─────────────────────────────────────────────────────────────────────┘

For each minority sample:
1. Find k nearest neighbors (k=5)
2. Select random neighbor
3. Create synthetic sample between them
4. Repeat until balanced

                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    AFTER SMOTE                                       │
└─────────────────────────────────────────────────────────────────────┘

Training Data Distribution:
Cluster 0: ████████████████████ (100 samples)
Cluster 1: ████████████████████ (100 samples) ← Oversampled
Cluster 2: ████████████████████ (100 samples)
Cluster 3: ████████████████████ (100 samples) ← Oversampled
Cluster 4: ████████████████████ (100 samples) ← Oversampled

Result: Balanced training, better predictions for all clusters
```

---

## 📈 Feature Importance Visualization

```
┌─────────────────────────────────────────────────────────────────────┐
│              TOP 5 FEATURES (Weight Loss Model)                      │
└─────────────────────────────────────────────────────────────────────┘

Calories        ████████████████████████████████████ 0.35
Fats            ██████████████████████ 0.22
Proteins        ████████████████ 0.18
Carbohydrates   ████████████ 0.12
Fibre           ████████ 0.08

Interpretation:
- Calories is the most important feature (35%)
- Fats and Proteins are also significant
- Model focuses on macronutrients for weight loss
- Can be visualized in frontend dashboard
```

---

## 🎨 Frontend Integration Points

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FRONTEND DASHBOARD                                │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │   Feature    │  │    Model     │  │  Dataset     │
        │  Importance  │  │  Performance │  │    Stats     │
        │   Chart      │  │   Metrics    │  │   Display    │
        └──────────────┘  └──────────────┘  └──────────────┘
                │                 │                 │
                ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ Bar chart of │  │ Accuracy:    │  │ Total Foods: │
    │ top features │  │   85%        │  │   600+       │
    │              │  │ Precision:   │  │ Vegetarian:  │
    │ Data source: │  │   82%        │  │   400+       │
    │ model_       │  │ Recall:      │  │ Non-veg:     │
    │ insights.json│  │   80%        │  │   200+       │
    │              │  │              │  │              │
    │              │  │ Data source: │  │ Data source: │
    │              │  │ model_       │  │ food_        │
    │              │  │ eval.json    │  │ master.csv   │
    └──────────────┘  └──────────────┘  └──────────────┘
```

---

## 🔄 Complete Setup Flow

```
START
  │
  ▼
┌─────────────────────┐
│ Install Dependencies│
│ pip install -r      │
│ requirements.txt    │
└─────────────────────┘
  │
  ▼
┌─────────────────────┐
│ Fetch USDA Foods    │
│ python scripts/     │
│ fetch_usda_foods.py │
└─────────────────────┘
  │
  ▼
┌─────────────────────┐
│ Merge Datasets      │
│ python scripts/     │
│ merge_datasets.py   │
└─────────────────────┘
  │
  ▼
┌─────────────────────┐
│ Run Migrations      │
│ python manage.py    │
│ migrate             │
└─────────────────────┘
  │
  ▼
┌─────────────────────┐
│ Evaluate Model      │
│ python scripts/     │
│ evaluate_model.py   │
└─────────────────────┘
  │
  ▼
┌─────────────────────┐
│ Start Server        │
│ python manage.py    │
│ runserver           │
└─────────────────────┘
  │
  ▼
END (Ready to use!)
```

---

## 📊 Performance Metrics Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    5-FOLD CROSS-VALIDATION                           │
└─────────────────────────────────────────────────────────────────────┘

Dataset Split:
┌──────┬──────┬──────┬──────┬──────┐
│ Fold1│ Fold2│ Fold3│ Fold4│ Fold5│
└──────┴──────┴──────┴──────┴──────┘

Iteration 1: Train on [2,3,4,5], Test on [1]
Iteration 2: Train on [1,3,4,5], Test on [2]
Iteration 3: Train on [1,2,4,5], Test on [3]
Iteration 4: Train on [1,2,3,5], Test on [4]
Iteration 5: Train on [1,2,3,4], Test on [5]

For each iteration:
  ├─ Apply SMOTE to training set
  ├─ Train Random Forest
  ├─ Predict on test set
  └─ Calculate metrics

Final Results:
  ├─ Mean accuracy ± std
  ├─ Mean precision ± std
  ├─ Mean recall ± std
  └─ Mean F1-score ± std

Save to model_eval.json
```

---

This visual guide shows the complete data flow, algorithm improvements, and integration points for the EatRight ML system.
