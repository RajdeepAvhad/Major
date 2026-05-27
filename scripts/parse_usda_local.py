"""
USDA Local CSV Parser
Parses USDA Foundation Foods CSV files (food.csv, food_nutrient.csv, food_category.csv)
Joins, pivots, and outputs in EatRight format
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Add parent directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# File paths
USDA_DIR = BASE_DIR / 'static' / 'data' / 'usda'
FOOD_CSV = USDA_DIR / 'food1.csv'
FOOD_NUTRIENT_CSV = USDA_DIR / 'food_nutrient.csv'
FOOD_CATEGORY_CSV = USDA_DIR / 'food_category.csv'
OUTPUT_PATH = BASE_DIR / 'static' / 'data' / 'food_expanded.csv'

# Nutrient ID mapping (USDA → EatRight)
NUTRIENT_MAPPING = {
    1008: 'Calories',
    1003: 'Proteins',
    1004: 'Fats',
    1005: 'Carbohydrates',
    1079: 'Fibre',
    2000: 'Sugars',
    1087: 'Calcium',
    1089: 'Iron',
    1093: 'Sodium',
    1092: 'Potassium',
    1114: 'VitaminD'
}

# Food categories to include
TARGET_CATEGORIES = [
    'Vegetables and Vegetable Products',
    'Fruits and Fruit Juices',
    'Legumes and Legume Products',
    'Poultry Products',
    'Finfish and Shellfish Products',
    'Dairy and Egg Products',
    'Cereal Grains and Pasta',
    'Nut and Seed Products'
]


def check_files_exist():
    """Check if all required USDA CSV files exist"""
    print("Checking USDA CSV files...")
    print("=" * 60)
    
    files = {
        'food1.csv': FOOD_CSV,
        'food_nutrient.csv': FOOD_NUTRIENT_CSV,
        'food_category.csv': FOOD_CATEGORY_CSV
    }
    
    all_exist = True
    for name, path in files.items():
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"✓ {name}: {size_mb:.1f} MB")
        else:
            print(f"✗ {name}: NOT FOUND")
            print(f"   Expected at: {path}")
            all_exist = False
    
    if not all_exist:
        print("\n❌ ERROR: Missing USDA CSV files!")
        print("\nPlease ensure all files are in:")
        print(f"   {USDA_DIR}")
        return False
    
    return True


def load_food_categories():
    """Load and process food categories"""
    print("\nLoading food categories...")
    print("=" * 60)
    
    try:
        df = pd.read_csv(FOOD_CATEGORY_CSV, low_memory=False)
        print(f"✓ Loaded {len(df)} categories")
        
        # Show available columns
        print(f"Columns: {list(df.columns)}")
        
        # Filter to target categories
        df_filtered = df[df['description'].isin(TARGET_CATEGORIES)]
        print(f"✓ Filtered to {len(df_filtered)} target categories:")
        for cat in df_filtered['description'].unique():
            print(f"  - {cat}")
        
        return df_filtered
    
    except Exception as e:
        print(f"❌ Error loading categories: {e}")
        return None


def load_foods(category_df):
    """Load foods and join with categories"""
    print("\nLoading foods...")
    print("=" * 60)
    
    try:
        df = pd.read_csv(FOOD_CSV, low_memory=False)
        print(f"✓ Loaded {len(df)} foods")
        print(f"Columns: {list(df.columns)}")
        
        # Join with categories
        df = df.merge(
            category_df[['id', 'description']],
            left_on='food_category_id',
            right_on='id',
            how='inner'
        )
        
        # Rename category description column
        df = df.rename(columns={'description_y': 'category', 'description_x': 'food_name'})
        
        print(f"✓ Joined with categories: {len(df)} foods")
        
        # Show category breakdown
        print("\nCategory breakdown:")
        for cat, count in df['category'].value_counts().items():
            print(f"  {cat}: {count} items")
        
        return df[['fdc_id', 'food_name', 'category']]
    
    except Exception as e:
        print(f"❌ Error loading foods: {e}")
        return None


def load_and_pivot_nutrients():
    """Load food_nutrient.csv and pivot to wide format"""
    print("\nLoading and pivoting nutrients...")
    print("=" * 60)
    
    try:
        df = pd.read_csv(FOOD_NUTRIENT_CSV, low_memory=False)
        print(f"✓ Loaded {len(df)} nutrient records")
        print(f"Columns: {list(df.columns)}")
        
        # Filter to only nutrients we care about
        df = df[df['nutrient_id'].isin(NUTRIENT_MAPPING.keys())]
        print(f"✓ Filtered to {len(df)} relevant nutrient records")
        
        # Map nutrient IDs to our column names
        df['nutrient_name'] = df['nutrient_id'].map(NUTRIENT_MAPPING)
        
        # Pivot: rows=fdc_id, columns=nutrient_name, values=amount
        df_pivot = df.pivot_table(
            index='fdc_id',
            columns='nutrient_name',
            values='amount',
            aggfunc='first'  # Take first value if duplicates
        ).reset_index()
        
        print(f"✓ Pivoted to {len(df_pivot)} foods with nutrients")
        print(f"Nutrient columns: {[col for col in df_pivot.columns if col != 'fdc_id']}")
        
        return df_pivot
    
    except Exception as e:
        print(f"❌ Error loading nutrients: {e}")
        return None


def merge_all_data(foods_df, nutrients_df):
    """Merge foods with nutrients"""
    print("\nMerging foods with nutrients...")
    print("=" * 60)
    
    try:
        df = foods_df.merge(nutrients_df, on='fdc_id', how='inner')
        print(f"✓ Merged: {len(df)} foods with complete data")
        
        return df
    
    except Exception as e:
        print(f"❌ Error merging data: {e}")
        return None


def set_meal_flags(df):
    """Set Breakfast/Lunch/Dinner flags based on category"""
    print("\nSetting meal flags...")
    print("=" * 60)
    
    # Initialize all flags
    df['Breakfast'] = 0
    df['Lunch'] = 1
    df['Dinner'] = 1
    
    # Set Breakfast=1 for Cereal and Dairy
    breakfast_categories = ['Cereal Grains and Pasta', 'Dairy and Egg Products']
    df.loc[df['category'].isin(breakfast_categories), 'Breakfast'] = 1
    
    print(f"✓ Breakfast items: {df['Breakfast'].sum()}")
    print(f"✓ Lunch items: {df['Lunch'].sum()}")
    print(f"✓ Dinner items: {df['Dinner'].sum()}")
    
    return df


def set_veg_nonveg(df):
    """Set VegNovVeg based on category"""
    print("\nSetting vegetarian flags...")
    print("=" * 60)
    
    # Default to Veg (0)
    df['VegNovVeg'] = 0
    
    # Set NonVeg (1) for Poultry and Fish
    nonveg_categories = ['Poultry Products', 'Finfish and Shellfish Products']
    df.loc[df['category'].isin(nonveg_categories), 'VegNovVeg'] = 1
    
    veg_count = len(df[df['VegNovVeg'] == 0])
    nonveg_count = len(df[df['VegNovVeg'] == 1])
    
    print(f"✓ Vegetarian items: {veg_count}")
    print(f"✓ Non-vegetarian items: {nonveg_count}")
    
    return df


def clean_and_format(df):
    """Clean data and format to match food.csv structure"""
    print("\nCleaning and formatting...")
    print("=" * 60)
    
    # Rename food_name to Food_items
    df = df.rename(columns={'food_name': 'Food_items'})
    
    # Fill missing nutrient values with 0
    nutrient_cols = ['Calories', 'Fats', 'Proteins', 'Iron', 'Calcium', 
                     'Sodium', 'Potassium', 'Carbohydrates', 'Fibre', 
                     'VitaminD', 'Sugars']
    
    for col in nutrient_cols:
        if col not in df.columns:
            df[col] = 0
        else:
            df[col] = df[col].fillna(0)
    
    # Round nutrient values to 1 decimal place
    for col in nutrient_cols:
        df[col] = df[col].round(1)
    
    # Remove foods with zero calories
    original_count = len(df)
    df = df[df['Calories'] > 0]
    removed = original_count - len(df)
    print(f"✓ Removed {removed} foods with zero calories")
    
    # Cap extreme values
    df['Calories'] = df['Calories'].clip(upper=900)
    df['Fats'] = df['Fats'].clip(upper=100)
    df['Proteins'] = df['Proteins'].clip(upper=100)
    df['Carbohydrates'] = df['Carbohydrates'].clip(upper=100)
    
    # Clean food names
    df['Food_items'] = df['Food_items'].str.strip().str.title()
    
    # Remove duplicates by food name
    original_count = len(df)
    df = df.drop_duplicates(subset=['Food_items'], keep='first')
    removed = original_count - len(df)
    print(f"✓ Removed {removed} duplicate food names")
    
    # Select and order columns to match food.csv exactly
    output_columns = [
        'Food_items', 'Breakfast', 'Lunch', 'Dinner', 'VegNovVeg',
        'Calories', 'Fats', 'Proteins', 'Iron', 'Calcium', 'Sodium',
        'Potassium', 'Carbohydrates', 'Fibre', 'VitaminD', 'Sugars'
    ]
    
    df = df[output_columns]
    
    # Sort by food name
    df = df.sort_values('Food_items').reset_index(drop=True)
    
    print(f"✓ Final dataset: {len(df)} foods")
    
    return df


def save_to_csv(df):
    """Save to food_expanded.csv"""
    print("\nSaving to CSV...")
    print("=" * 60)
    
    # Create output directory if needed
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    df.to_csv(OUTPUT_PATH, index=False)
    
    print(f"✓ Saved to: {OUTPUT_PATH}")
    print(f"  Total foods: {len(df)}")
    print(f"  File size: {OUTPUT_PATH.stat().st_size / 1024:.1f} KB")
    
    # Show sample
    print("\nSample foods:")
    for i, row in df.head(5).iterrows():
        print(f"  {row['Food_items']}: {row['Calories']} cal, {row['Proteins']}g protein")


def main():
    """Main execution function"""
    print("USDA Local CSV Parser")
    print("=" * 60)
    
    # Check files exist
    if not check_files_exist():
        return
    
    # Load food categories
    category_df = load_food_categories()
    if category_df is None or category_df.empty:
        return
    
    # Load foods and join with categories
    foods_df = load_foods(category_df)
    if foods_df is None or foods_df.empty:
        return
    
    # Load and pivot nutrients
    nutrients_df = load_and_pivot_nutrients()
    if nutrients_df is None or nutrients_df.empty:
        return
    
    # Merge all data
    df = merge_all_data(foods_df, nutrients_df)
    if df is None or df.empty:
        return
    
    # Set meal flags
    df = set_meal_flags(df)
    
    # Set veg/non-veg
    df = set_veg_nonveg(df)
    
    # Clean and format
    df = clean_and_format(df)
    
    # Save to CSV
    save_to_csv(df)
    
    print("\n" + "=" * 60)
    print("✓ USDA parsing completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run: python scripts/merge_datasets.py")
    print("2. Run: python manage.py migrate")
    print("3. Run: python scripts/evaluate_model.py")


if __name__ == "__main__":
    main()
