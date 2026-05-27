"""
Dataset Merging Script
Merges food.csv + food_expanded.csv + indian_foods.csv
Deduplicates, normalizes, and creates master dataset
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Add parent directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

DATA_DIR = BASE_DIR / 'static' / 'data'


def load_datasets():
    """
    Load all three datasets
    """
    print("Loading datasets...")
    print("=" * 60)
    
    datasets = {}
    
    # Load original food.csv
    food_path = DATA_DIR / 'food.csv'
    if food_path.exists():
        datasets['original'] = pd.read_csv(food_path)
        print(f"✓ Loaded food.csv: {len(datasets['original'])} items")
    else:
        print(f"✗ food.csv not found at {food_path}")
        datasets['original'] = pd.DataFrame()
    
    # Load USDA expanded foods
    expanded_path = DATA_DIR / 'food_expanded.csv'
    if expanded_path.exists():
        datasets['expanded'] = pd.read_csv(expanded_path)
        print(f"✓ Loaded food_expanded.csv: {len(datasets['expanded'])} items")
    else:
        print(f"⚠ food_expanded.csv not found (run fetch_usda_foods.py first)")
        datasets['expanded'] = pd.DataFrame()
    
    # Load Indian foods
    indian_path = DATA_DIR / 'indian_foods.csv'
    if indian_path.exists():
        datasets['indian'] = pd.read_csv(indian_path)
        print(f"✓ Loaded indian_foods.csv: {len(datasets['indian'])} items")
    else:
        print(f"✗ indian_foods.csv not found at {indian_path}")
        datasets['indian'] = pd.DataFrame()
    
    return datasets


def standardize_columns(df):
    """
    Ensure all required columns exist with proper data types
    """
    required_columns = [
        'Food_items', 'Breakfast', 'Lunch', 'Dinner', 'VegNovVeg',
        'Calories', 'Fats', 'Proteins', 'Iron', 'Calcium', 'Sodium',
        'Potassium', 'Carbohydrates', 'Fibre', 'VitaminD', 'Sugars'
    ]
    
    # Add missing columns with default values
    for col in required_columns:
        if col not in df.columns:
            if col in ['Breakfast', 'Lunch', 'Dinner', 'VegNovVeg']:
                df[col] = 0
            elif col == 'Food_items':
                df[col] = 'Unknown'
            else:
                df[col] = 0.0
    
    # Ensure correct column order
    df = df[required_columns]
    
    # Convert data types
    df['Food_items'] = df['Food_items'].astype(str)
    
    # Binary columns
    for col in ['Breakfast', 'Lunch', 'Dinner', 'VegNovVeg']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    # Numeric columns
    numeric_cols = ['Calories', 'Fats', 'Proteins', 'Iron', 'Calcium', 
                    'Sodium', 'Potassium', 'Carbohydrates', 'Fibre', 
                    'VitaminD', 'Sugars']
    
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return df


def clean_food_names(df):
    """
    Clean and standardize food names
    """
    df['Food_items'] = df['Food_items'].str.strip()
    df['Food_items'] = df['Food_items'].str.title()
    
    # Remove extra whitespace
    df['Food_items'] = df['Food_items'].str.replace(r'\s+', ' ', regex=True)
    
    return df


def merge_datasets(datasets):
    """
    Merge all datasets and remove duplicates
    """
    print("\nMerging datasets...")
    print("=" * 60)
    
    # Combine all non-empty dataframes
    dfs_to_merge = []
    
    for name, df in datasets.items():
        if not df.empty:
            df = standardize_columns(df)
            df = clean_food_names(df)
            dfs_to_merge.append(df)
            print(f"  Prepared {name}: {len(df)} items")
    
    if not dfs_to_merge:
        print("❌ No datasets to merge!")
        return pd.DataFrame()
    
    # Concatenate all dataframes
    merged_df = pd.concat(dfs_to_merge, ignore_index=True)
    print(f"\n✓ Combined total: {len(merged_df)} items")
    
    # Remove duplicates (keep first occurrence)
    original_count = len(merged_df)
    merged_df = merged_df.drop_duplicates(subset=['Food_items'], keep='first')
    duplicates_removed = original_count - len(merged_df)
    
    print(f"✓ Removed {duplicates_removed} duplicates")
    print(f"✓ Final unique items: {len(merged_df)}")
    
    return merged_df


def normalize_nutrients(df):
    """
    Normalize nutrient values to reasonable ranges
    """
    print("\nNormalizing nutrient values...")
    print("=" * 60)
    
    # Define reasonable ranges per 100g (outliers will be capped)
    nutrient_ranges = {
        'Calories': (0, 900),      # Max: oils/fats
        'Fats': (0, 100),          # Max: pure fat
        'Proteins': (0, 100),      # Max: protein powder
        'Iron': (0, 50),           # Max: fortified foods
        'Calcium': (0, 1500),      # Max: cheese/dairy
        'Sodium': (0, 5000),       # Max: salt/processed
        'Potassium': (0, 3500),    # Max: dried herbs
        'Carbohydrates': (0, 100), # Max: sugar/starch
        'Fibre': (0, 80),          # Max: bran/seeds
        'VitaminD': (0, 100),      # Max: fortified foods
        'Sugars': (0, 100)         # Max: pure sugar
    }
    
    for nutrient, (min_val, max_val) in nutrient_ranges.items():
        if nutrient in df.columns:
            # Cap values at min/max
            df[nutrient] = df[nutrient].clip(lower=min_val, upper=max_val)
            
            # Round to 2 decimal places
            df[nutrient] = df[nutrient].round(2)
    
    # Remove rows with zero calories (likely incomplete data)
    original_count = len(df)
    df = df[df['Calories'] > 0]
    removed = original_count - len(df)
    
    if removed > 0:
        print(f"✓ Removed {removed} items with zero calories")
    
    print(f"✓ Normalized {len(df)} food items")
    
    return df


def add_statistics(df):
    """
    Print dataset statistics
    """
    print("\nDataset Statistics:")
    print("=" * 60)
    
    print(f"Total food items: {len(df)}")
    print(f"\nMeal distribution:")
    print(f"  Breakfast items: {df['Breakfast'].sum()}")
    print(f"  Lunch items: {df['Lunch'].sum()}")
    print(f"  Dinner items: {df['Dinner'].sum()}")
    
    print(f"\nDiet type:")
    print(f"  Vegetarian: {len(df[df['VegNovVeg'] == 0])}")
    print(f"  Non-vegetarian: {len(df[df['VegNovVeg'] == 1])}")
    
    print(f"\nNutrient ranges (per 100g):")
    nutrients = ['Calories', 'Proteins', 'Fats', 'Carbohydrates', 'Fibre']
    for nutrient in nutrients:
        if nutrient in df.columns:
            print(f"  {nutrient}: {df[nutrient].min():.1f} - {df[nutrient].max():.1f} "
                  f"(avg: {df[nutrient].mean():.1f})")


def save_master_dataset(df, output_path):
    """
    Save the master dataset
    """
    print("\nSaving master dataset...")
    print("=" * 60)
    
    # Sort by food name
    df = df.sort_values('Food_items').reset_index(drop=True)
    
    # Save to CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"✓ Saved master dataset to: {output_path}")
    print(f"  Total items: {len(df)}")
    print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")


def main():
    """
    Main execution function
    """
    print("EatRight Dataset Merger")
    print("=" * 60)
    
    # Load all datasets
    datasets = load_datasets()
    
    if all(df.empty for df in datasets.values()):
        print("\n❌ No datasets found to merge!")
        return
    
    # Merge datasets
    merged_df = merge_datasets(datasets)
    
    if merged_df.empty:
        print("\n❌ Merge failed!")
        return
    
    # Normalize nutrients
    normalized_df = normalize_nutrients(merged_df)
    
    # Print statistics
    add_statistics(normalized_df)
    
    # Save master dataset
    output_path = DATA_DIR / 'food_master.csv'
    save_master_dataset(normalized_df, output_path)
    
    print("\n" + "=" * 60)
    print("✓ Dataset merge completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Update recommender/functions.py to use food_master.csv")
    print("2. Run scripts/evaluate_model.py to test the new model")


if __name__ == "__main__":
    main()
