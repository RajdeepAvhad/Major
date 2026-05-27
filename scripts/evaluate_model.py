"""
Model Evaluation Script
Cross-validates Random Forest model with 5-fold CV
Evaluates accuracy, precision, recall, and F1-score
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import cross_validate, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.cluster import AgglomerativeClustering
from imblearn.over_sampling import SMOTE

# Add parent directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))


def load_data():
    """
    Load food and nutrition distribution data
    """
    print("Loading datasets...")
    print("=" * 60)
    
    # Load master food dataset
    food_path = BASE_DIR / 'static' / 'data' / 'food_master.csv'
    if not food_path.exists():
        food_path = BASE_DIR / 'static' / 'data' / 'food.csv'
        print(f"⚠ Using fallback: {food_path}")
    
    food_data = pd.read_csv(food_path)
    print(f"✓ Loaded food data: {len(food_data)} items")
    
    # Load nutrition distribution
    nutrition_path = BASE_DIR / 'static' / 'data' / 'nutrition_distriution.csv'
    nutrition_data = pd.read_csv(nutrition_path)
    print(f"✓ Loaded nutrition distribution: {nutrition_data.shape}")
    
    return food_data, nutrition_data


def prepare_training_data(food_data, nutrition_data):
    """
    Prepare training data similar to functions.py logic
    """
    print("\nPreparing training data...")
    print("=" * 60)
    
    # Separate foods by meal type
    breakfast_foods = food_data[food_data['Breakfast'] == 1]
    lunch_foods = food_data[food_data['Lunch'] == 1]
    dinner_foods = food_data[food_data['Dinner'] == 1]
    
    print(f"Breakfast foods: {len(breakfast_foods)}")
    print(f"Lunch foods: {len(lunch_foods)}")
    print(f"Dinner foods: {len(dinner_foods)}")
    
    # Extract nutrient columns (columns 5-14 in original format)
    nutrient_cols = ['Calories', 'Fats', 'Proteins', 'Iron', 'Calcium', 
                     'Sodium', 'Potassium', 'Carbohydrates', 'Fibre', 'VitaminD']
    
    # Prepare data for clustering
    breakfast_nutrients = breakfast_foods[nutrient_cols].values
    lunch_nutrients = lunch_foods[nutrient_cols].values
    dinner_nutrients = dinner_foods[nutrient_cols].values
    
    # Apply Agglomerative Clustering
    print("\nApplying Agglomerative Clustering (n_clusters=5)...")
    
    brk_clustering = AgglomerativeClustering(n_clusters=5, linkage='ward')
    brk_labels = brk_clustering.fit_predict(breakfast_nutrients)
    
    lunch_clustering = AgglomerativeClustering(n_clusters=5, linkage='ward')
    lunch_labels = lunch_clustering.fit_predict(lunch_nutrients)
    
    dinner_clustering = AgglomerativeClustering(n_clusters=5, linkage='ward')
    dinner_labels = dinner_clustering.fit_predict(dinner_nutrients)
    
    print(f"✓ Breakfast clusters: {np.unique(brk_labels)}")
    print(f"✓ Lunch clusters: {np.unique(lunch_labels)}")
    print(f"✓ Dinner clusters: {np.unique(dinner_labels)}")
    
    return {
        'breakfast': (breakfast_nutrients, brk_labels),
        'lunch': (lunch_nutrients, lunch_labels),
        'dinner': (dinner_nutrients, dinner_labels)
    }


def create_synthetic_training_set(nutrients, labels, nutrition_data):
    """
    Create synthetic training set with BMI and age classes
    Similar to the logic in functions.py
    """
    # Extract weight loss category from nutrition distribution
    dataTog = nutrition_data.T
    weightlosscat = dataTog.iloc[[1, 2, 7, 8]]
    weightlosscat = weightlosscat.T
    weightlosscat_data = weightlosscat.to_numpy()[1:, :]
    
    # BMI and age classes
    bmicls = [0, 1, 2, 3, 4]
    agecls = [0, 1, 2, 3, 4]
    
    # Create training data - one sample per (food, BMI, age) combination
    X_train_list = []
    y_train_list = []
    
    # For each BMI class
    for bmi_class in bmicls:
        # For each food item that has a label
        for jj in range(min(len(weightlosscat_data), len(labels))):
            valloc = list(weightlosscat_data[jj])
            valloc.append(bmi_class)
            valloc.append(agecls[bmi_class])  # Use corresponding age class
            X_train_list.append(valloc)
            y_train_list.append(labels[jj])
    
    # Convert to numpy arrays
    X_train = np.array(X_train_list, dtype=np.float32)
    y_train = np.array(y_train_list)
    
    return X_train, y_train


def evaluate_model_cv(X, y, model_name='model'):
    """
    Evaluate model using 5-fold cross-validation
    """
    print(f"\nEvaluating {model_name}...")
    print("=" * 60)
    
    # Check class distribution
    unique_classes, class_counts = np.unique(y, return_counts=True)
    print(f"Classes: {unique_classes}")
    print(f"Class distribution: {dict(zip(unique_classes, class_counts))}")
    
    # Ensure we have enough samples for 5-fold CV
    min_samples = class_counts.min()
    n_splits = min(5, min_samples)
    
    if n_splits < 2:
        print(f"⚠ Insufficient samples for CV (min={min_samples}). Skipping.")
        return None
    
    print(f"Using {n_splits}-fold cross-validation")
    
    # Apply SMOTE if needed
    if min_samples >= 2 and len(unique_classes) > 1:
        try:
            smote = SMOTE(random_state=42, k_neighbors=min(5, min_samples - 1))
            X_resampled, y_resampled = smote.fit_resample(X, y)
            print(f"✓ SMOTE applied: {len(X)} → {len(X_resampled)} samples")
        except Exception as e:
            print(f"⚠ SMOTE failed: {e}")
            X_resampled, y_resampled = X, y
    else:
        X_resampled, y_resampled = X, y
    
    # Create Random Forest classifier
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    
    # Define scoring metrics
    scoring = {
        'accuracy': 'accuracy',
        'precision_macro': 'precision_macro',
        'recall_macro': 'recall_macro',
        'f1_macro': 'f1_macro'
    }
    
    # Perform cross-validation
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    
    try:
        cv_results = cross_validate(
            clf, X_resampled, y_resampled,
            cv=cv,
            scoring=scoring,
            return_train_score=True
        )
        
        # Calculate mean and std for each metric
        results = {
            'accuracy': {
                'mean': float(cv_results['test_accuracy'].mean()),
                'std': float(cv_results['test_accuracy'].std()),
                'scores': cv_results['test_accuracy'].tolist()
            },
            'precision': {
                'mean': float(cv_results['test_precision_macro'].mean()),
                'std': float(cv_results['test_precision_macro'].std()),
                'scores': cv_results['test_precision_macro'].tolist()
            },
            'recall': {
                'mean': float(cv_results['test_recall_macro'].mean()),
                'std': float(cv_results['test_recall_macro'].std()),
                'scores': cv_results['test_recall_macro'].tolist()
            },
            'f1_score': {
                'mean': float(cv_results['test_f1_macro'].mean()),
                'std': float(cv_results['test_f1_macro'].std()),
                'scores': cv_results['test_f1_macro'].tolist()
            }
        }
        
        # Print results
        print(f"\n{model_name} Results:")
        print(f"  Accuracy:  {results['accuracy']['mean']:.4f} ± {results['accuracy']['std']:.4f}")
        print(f"  Precision: {results['precision']['mean']:.4f} ± {results['precision']['std']:.4f}")
        print(f"  Recall:    {results['recall']['mean']:.4f} ± {results['recall']['std']:.4f}")
        print(f"  F1-Score:  {results['f1_score']['mean']:.4f} ± {results['f1_score']['std']:.4f}")
        
        return results
    
    except Exception as e:
        print(f"❌ Cross-validation failed: {e}")
        return None


def save_evaluation_results(all_results, output_path):
    """
    Save evaluation results to JSON file
    """
    print("\nSaving evaluation results...")
    print("=" * 60)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"✓ Results saved to: {output_path}")


def main():
    """
    Main execution function
    """
    print("EatRight Model Evaluation")
    print("=" * 60)
    
    # Load data
    food_data, nutrition_data = load_data()
    
    # Prepare training data
    meal_data = prepare_training_data(food_data, nutrition_data)
    
    # Evaluate each meal type
    all_results = {}
    
    for meal_type, (nutrients, labels) in meal_data.items():
        try:
            # Create synthetic training set
            X_train, y_train = create_synthetic_training_set(
                nutrients, labels, nutrition_data
            )
            
            # Evaluate model
            results = evaluate_model_cv(X_train, y_train, model_name=meal_type)
            
            if results:
                all_results[meal_type] = results
        
        except Exception as e:
            print(f"❌ Error evaluating {meal_type}: {e}")
    
    # Add metadata
    all_results['metadata'] = {
        'total_foods': len(food_data),
        'clustering_algorithm': 'AgglomerativeClustering',
        'n_clusters': 5,
        'linkage': 'ward',
        'classifier': 'RandomForestClassifier',
        'n_estimators': 100,
        'oversampling': 'SMOTE',
        'cv_folds': 5
    }
    
    # Save results
    output_path = BASE_DIR / 'static' / 'data' / 'model_eval.json'
    save_evaluation_results(all_results, output_path)
    
    print("\n" + "=" * 60)
    print("✓ Model evaluation completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
