"""
USDA FoodData Central API Integration Script
Fetches 500+ food items from USDA database and maps to EatRight schema
"""

import os
import sys
import json
import time
import requests
import pandas as pd
from pathlib import Path

# Add parent directory to path for Django imports
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

USDA_API_KEY = os.getenv('USDA_API_KEY')
USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

# USDA Nutrient ID mapping to our schema
NUTRIENT_MAP = {
    1008: 'Calories',      # Energy (kcal)
    1003: 'Proteins',      # Protein (g)
    1004: 'Fats',          # Total lipid (fat) (g)
    1005: 'Carbohydrates', # Carbohydrate, by difference (g)
    1079: 'Fibre',         # Fiber, total dietary (g)
    2000: 'Sugars',        # Sugars, total including NLEA (g)
    1087: 'Calcium',       # Calcium, Ca (mg)
    1089: 'Iron',          # Iron, Fe (mg)
    1093: 'Sodium',        # Sodium, Na (mg)
    1092: 'Potassium',     # Potassium, K (mg)
    1114: 'VitaminD',      # Vitamin D (D2 + D3) (µg)
}

# Food categories to fetch
FOOD_CATEGORIES = {
    'fruits': ['apple', 'banana', 'orange', 'grape', 'strawberry', 'blueberry', 'mango', 
               'pineapple', 'watermelon', 'papaya', 'kiwi', 'peach', 'pear', 'plum', 
               'cherry', 'apricot', 'pomegranate', 'guava', 'lychee', 'dragon fruit'],
    
    'vegetables': ['broccoli', 'spinach', 'carrot', 'tomato', 'cucumber', 'bell pepper', 
                   'cauliflower', 'cabbage', 'lettuce', 'kale', 'zucchini', 'eggplant',
                   'mushroom', 'onion', 'garlic', 'potato', 'sweet potato', 'pumpkin',
                   'beetroot', 'radish', 'celery', 'asparagus', 'green beans'],
    
    'grains': ['rice', 'wheat bread', 'oats', 'quinoa', 'barley', 'corn', 'pasta',
               'whole wheat bread', 'brown rice', 'couscous', 'bulgur', 'millet',
               'buckwheat', 'rye bread', 'bagel', 'tortilla', 'pita bread'],
    
    'proteins': ['chicken breast', 'salmon', 'tuna', 'beef', 'pork', 'turkey', 'shrimp',
                 'cod', 'tilapia', 'lamb', 'duck', 'sardines', 'mackerel', 'halibut',
                 'ground beef', 'chicken thigh', 'bacon', 'sausage', 'ham'],
    
    'dairy': ['milk', 'yogurt', 'cheese', 'cottage cheese', 'greek yogurt', 'cheddar cheese',
              'mozzarella', 'parmesan', 'butter', 'cream cheese', 'sour cream', 'whey protein',
              'ice cream', 'kefir', 'ricotta cheese'],
    
    'legumes': ['lentils', 'chickpeas', 'black beans', 'kidney beans', 'pinto beans',
                'navy beans', 'lima beans', 'soybeans', 'green peas', 'split peas',
                'edamame', 'tofu', 'tempeh', 'peanuts', 'almonds', 'cashews', 'walnuts']
}


def fetch_food_from_usda(query, max_results=5):
    """
    Fetch food data from USDA FoodData Central API
    """
    if not USDA_API_KEY:
        print("ERROR: USDA_API_KEY not found in environment variables")
        return []
    
    params = {
        'api_key': USDA_API_KEY,
        'query': query,
        'pageSize': max_results,
        'dataType': ['Survey (FNDDS)', 'Foundation', 'SR Legacy']  # Prioritize complete data
    }
    
    try:
        response = requests.get(USDA_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        foods = []
        if 'foods' in data:
            for food_item in data['foods']:
                parsed = parse_usda_food(food_item, query)
                if parsed:
                    foods.append(parsed)
        
        return foods
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {query}: {e}")
        return []


def parse_usda_food(food_item, original_query):
    """
    Parse USDA food item and extract nutrients
    """
    try:
        food_name = food_item.get('description', original_query).title()
        
        # Initialize nutrient dictionary with zeros
        nutrients = {
            'Food_items': food_name,
            'Breakfast': 0,
            'Lunch': 0,
            'Dinner': 0,
            'VegNovVeg': 0,  # Will be set based on category
            'Calories': 0,
            'Fats': 0,
            'Proteins': 0,
            'Iron': 0,
            'Calcium': 0,
            'Sodium': 0,
            'Potassium': 0,
            'Carbohydrates': 0,
            'Fibre': 0,
            'VitaminD': 0,
            'Sugars': 0
        }
        
        # Extract nutrients from foodNutrients array
        if 'foodNutrients' in food_item:
            for nutrient in food_item['foodNutrients']:
                nutrient_id = nutrient.get('nutrientId')
                nutrient_value = nutrient.get('value', 0)
                
                if nutrient_id in NUTRIENT_MAP:
                    column_name = NUTRIENT_MAP[nutrient_id]
                    nutrients[column_name] = round(nutrient_value, 2)
        
        # Set meal flags based on food category
        nutrients = set_meal_flags(nutrients, original_query)
        
        return nutrients
    
    except Exception as e:
        print(f"Error parsing food item: {e}")
        return None


def set_meal_flags(nutrients, query):
    """
    Set Breakfast/Lunch/Dinner flags based on food category
    """
    query_lower = query.lower()
    food_name_lower = nutrients['Food_items'].lower()
    
    # Fruits - primarily breakfast
    if any(fruit in query_lower for fruit in FOOD_CATEGORIES['fruits']):
        nutrients['Breakfast'] = 1
        nutrients['VegNovVeg'] = 0  # Vegetarian
    
    # Vegetables - lunch and dinner
    elif any(veg in query_lower for veg in FOOD_CATEGORIES['vegetables']):
        nutrients['Lunch'] = 1
        nutrients['Dinner'] = 1
        nutrients['VegNovVeg'] = 0  # Vegetarian
    
    # Grains - all meals
    elif any(grain in query_lower for grain in FOOD_CATEGORIES['grains']):
        nutrients['Breakfast'] = 1
        nutrients['Lunch'] = 1
        nutrients['Dinner'] = 1
        nutrients['VegNovVeg'] = 0  # Vegetarian
    
    # Proteins - lunch and dinner
    elif any(protein in query_lower for protein in FOOD_CATEGORIES['proteins']):
        nutrients['Lunch'] = 1
        nutrients['Dinner'] = 1
        nutrients['VegNovVeg'] = 1  # Non-vegetarian
    
    # Dairy - breakfast and snacks
    elif any(dairy in query_lower for dairy in FOOD_CATEGORIES['dairy']):
        nutrients['Breakfast'] = 1
        nutrients['Lunch'] = 1
        nutrients['VegNovVeg'] = 0  # Vegetarian
    
    # Legumes - lunch and dinner
    elif any(legume in query_lower for legume in FOOD_CATEGORIES['legumes']):
        nutrients['Lunch'] = 1
        nutrients['Dinner'] = 1
        nutrients['VegNovVeg'] = 0  # Vegetarian
    
    else:
        # Default: available for all meals
        nutrients['Lunch'] = 1
        nutrients['Dinner'] = 1
    
    return nutrients


def fetch_all_foods():
    """
    Fetch foods from all categories
    """
    all_foods = []
    total_queries = sum(len(items) for items in FOOD_CATEGORIES.values())
    current = 0
    
    print(f"Starting USDA food fetch for {total_queries} queries...")
    print("=" * 60)
    
    for category, items in FOOD_CATEGORIES.items():
        print(f"\nFetching {category.upper()}...")
        
        for item in items:
            current += 1
            print(f"  [{current}/{total_queries}] Fetching: {item}...", end=" ")
            
            foods = fetch_food_from_usda(item, max_results=3)
            
            if foods:
                all_foods.extend(foods)
                print(f"✓ ({len(foods)} items)")
            else:
                print("✗ (no data)")
            
            # Rate limiting - USDA allows 1000 requests/hour
            time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print(f"Total foods fetched: {len(all_foods)}")
    
    return all_foods


def save_to_csv(foods, output_path):
    """
    Save foods to CSV file
    """
    if not foods:
        print("No foods to save!")
        return
    
    df = pd.DataFrame(foods)
    
    # Ensure column order matches original food.csv
    column_order = [
        'Food_items', 'Breakfast', 'Lunch', 'Dinner', 'VegNovVeg',
        'Calories', 'Fats', 'Proteins', 'Iron', 'Calcium', 'Sodium',
        'Potassium', 'Carbohydrates', 'Fibre', 'VitaminD', 'Sugars'
    ]
    
    df = df[column_order]
    
    # Remove duplicates based on food name
    df = df.drop_duplicates(subset=['Food_items'], keep='first')
    
    # Sort by food name
    df = df.sort_values('Food_items')
    
    # Save to CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"\n✓ Saved {len(df)} unique foods to: {output_path}")
    print(f"  - Vegetarian items: {len(df[df['VegNovVeg'] == 0])}")
    print(f"  - Non-vegetarian items: {len(df[df['VegNovVeg'] == 1])}")
    print(f"  - Breakfast items: {len(df[df['Breakfast'] == 1])}")
    print(f"  - Lunch items: {len(df[df['Lunch'] == 1])}")
    print(f"  - Dinner items: {len(df[df['Dinner'] == 1])}")


def main():
    """
    Main execution function
    """
    print("USDA FoodData Central - Food Fetcher")
    print("=" * 60)
    
    if not USDA_API_KEY:
        print("\n❌ ERROR: USDA_API_KEY not found in .env file")
        print("Please add your API key to .env:")
        print("USDA_API_KEY=your_key_here")
        print("\nGet your free API key at:")
        print("https://fdc.nal.usda.gov/api-key-signup.html")
        return
    
    # Fetch all foods
    foods = fetch_all_foods()
    
    if not foods:
        print("\n❌ No foods were fetched. Please check your API key and internet connection.")
        return
    
    # Save to CSV
    output_path = BASE_DIR / 'static' / 'data' / 'food_expanded.csv'
    save_to_csv(foods, output_path)
    
    print("\n" + "=" * 60)
    print("✓ USDA food fetch completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
