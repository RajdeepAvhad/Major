"""EatRight food image fetcher.

Lookup order:
1. Bundled local images under static/images/food
2. TheMealDB
3. Spoonacular recipe search
4. Spoonacular ingredient search

The script reads food_master.csv from the same folder as this script when present.
If that file is not present, it falls back to static/data/food_master.csv.
It writes food_master_with_images.csv and image_cache.json next to the script.
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

import pandas as pd
import requests


BASE_DIR = Path(__file__).resolve().parent
INPUT_CSV = BASE_DIR / "food_master.csv"
FALLBACK_INPUT_CSV = BASE_DIR / "static" / "data" / "food_master.csv"
OUTPUT_CSV = BASE_DIR / "food_master_with_images.csv"
CACHE_FILE = BASE_DIR / "image_cache.json"
SPOONACULAR_KEY = os.environ.get("SPOONACULAR_KEY", "")
DELAY = 0.5


KEYWORD_MAP = {
    "Aloo Sabzi": "aloo potato sabzi",
    "Bhaji Pav": "pav bhaji",
    "Chole Cooked": "chana masala",
    "Dal Cooked": "dal lentil soup",
    "Dal Makhani": "dal makhani",
    "Dosa": "dosa",
    "Idli": "idli",
    "Khichdi": "khichdi",
    "Palak Paneer": "palak paneer",
    "Paneer": "paneer",
    "Poha": "poha",
    "Rajma Cooked": "rajma curry",
    "Roti Wheat": "roti",
    "Sambar": "sambar",
    "Upma": "upma",
    "Uttapam": "uttapam",
    "Chappati": "chapati",
    "Basmati Rice Cooked": "basmati rice",
    "Almonds": "almonds",
    "Apples": "apple",
    "Apples, Fuji, With Skin, Raw": "apple",
    "Apples, Gala, With Skin, Raw": "apple",
    "Apples, Granny Smith, With Skin, Raw": "green apple",
    "Apples, Honeycrisp, With Skin, Raw": "apple",
    "Apples, Red Delicious, With Skin, Raw": "red apple",
    "Avocados": "avocado",
    "Banana Chips": "banana chips",
    "Bananas": "banana",
    "Bananas, Overripe, Raw": "banana",
    "Bananas, Ripe And Slightly Ripe, Raw": "banana",
    "Berries": "mixed berries",
    "Figs, Dried, Uncooked": "dried figs",
    "Grapes": "grapes",
    "Kiwifruit, Green, Raw": "kiwi fruit",
    "Melons, Cantaloupe, Raw": "cantaloupe melon",
    "Nectarines, Raw": "nectarine",
    "Orange": "orange fruit",
    "Orange Juice": "orange juice",
    "Oranges, Raw, Navels": "orange",
    "Oranges, Raw, Navels (Includes Foods For Usda'S Food Distribution Program)": "orange",
    "Pears": "pear",
    "Pears, Raw, Bartlett": "pear",
    "Pears, Raw, Bartlett (Includes Foods For Usda'S Food Distribution Program)": "pear",
    "Strawberries": "strawberries",
    "Strawberries, Raw": "strawberries",
    "Asparagus Cooked": "asparagus",
    "Beans": "green beans",
    "Beans, Snap, Green, Canned, Regular Pack, Drained Solids": "green beans",
    "Boiled Potatoes": "boiled potatoes",
    "Broccoli, Raw": "broccoli",
    "Brocolli": "broccoli",
    "Carrots, Frozen, Unprepared": "carrots",
    "Carrots, Frozen, Unprepared (Includes Foods For Usda'S Food Distribution Program)": "carrots",
    "Cauliflower": "cauliflower",
    "Corn": "corn",
    "Garlic, Raw": "garlic",
    "Hummus, Commercial": "hummus",
    "Kale, Frozen, Cooked, Boiled, Drained, Without Salt": "kale",
    "Kale, Raw": "kale",
    "Ketchup, Restaurant": "ketchup",
    "Lentils": "lentils",
    "Lettuce, Cos Or Romaine, Raw": "romaine lettuce",
    "Mushrooms": "mushrooms",
    "Olives, Green, Manzanilla, Stuffed With Pimiento": "green olives",
    "Onion Rings, Breaded, Par Fried, Frozen, Prepared, Heated In Oven": "onion rings",
    "Onions": "onion",
    "Onions, Red, Raw": "red onion",
    "Onions, White, Raw": "white onion",
    "Onions, Yellow, Raw": "onion",
    "Peas": "peas",
    "Pickles, Cucumber, Dill Or Kosher Dill": "pickles",
    "Pumpkin": "pumpkin",
    "Sweet Potatoes Cooked": "sweet potato",
    "Tomato": "tomato",
    "Tomatoes, Canned, Red, Ripe, Diced": "tomatoes",
    "Tomatoes, Grape, Raw": "cherry tomatoes",
    "Bagels Made In Wheat": "bagel",
    "Brown Rice": "brown rice",
    "Cereals-Corn Flakes": "corn flakes cereal",
    "Flour, Bread, White, Enriched, Unbleached": "bread flour",
    "Flour, Corn, Yellow, Fine Meal, Enriched": "corn flour",
    "Flour, Pastry, Unenriched, Unbleached": "flour",
    "Flour, Rice, Brown": "rice flour",
    "Flour, Rice, Glutinous": "glutinous rice",
    "Flour, Rice, White, Unenriched": "rice flour",
    "Flour, Soy, Defatted": "soy flour",
    "Flour, Soy, Full-Fat": "soy flour",
    "Flour, Wheat, All-Purpose, Enriched, Bleached": "wheat flour",
    "Flour, Wheat, All-Purpose, Enriched, Unbleached": "wheat flour",
    "Flour, Wheat, All-Purpose, Unenriched, Unbleached": "wheat flour",
    "Flour, Whole Wheat, Unenriched": "whole wheat flour",
    "French Fries": "french fries",
    "Mexican Rice": "mexican rice",
    "Noodles": "noodles",
    "Oat Bran Cooked": "oatmeal",
    "Pasta Canned With Tomato Sauce": "pasta tomato sauce",
    "Pasta With Corn Homemade": "pasta",
    "Quninoa": "quinoa",
    "White Rice": "white rice",
    "American Cheese": "american cheese",
    "Cheese, American, Restaurant": "american cheese",
    "Cheese, Cheddar": "cheddar cheese",
    "Cheese, Cottage, Lowfat, 2% Milkfat": "cottage cheese",
    "Cheese, Dry White, Queso Seco": "white cheese",
    "Cheese, Mozzarella, Low Moisture, Part-Skim": "mozzarella",
    "Cheese, Parmesan, Grated": "parmesan cheese",
    "Cheese, Pasteurized Process, American, Vitamin D Fortified": "american cheese",
    "Cheese, Ricotta, Whole Milk": "ricotta cheese",
    "Cheese, Swiss": "swiss cheese",
    "Chocolate Milk": "chocolate milk",
    "Cottage Cheese With Vegetables": "cottage cheese",
    "Egg Yolk Cooked": "egg yolk",
    "Egg, White, Dried": "egg white",
    "Egg, White, Raw, Frozen, Pasteurized": "egg white",
    "Egg, Whole, Dried": "eggs",
    "Egg, Whole, Raw, Frozen, Pasteurized": "eggs",
    "Egg, Yolk, Dried": "egg yolk",
    "Egg, Yolk, Raw, Frozen, Pasteurized": "egg yolk",
    "Eggs, Grade A, Large, Egg White": "egg white",
    "Eggs, Grade A, Large, Egg Whole": "whole eggs",
    "Eggs, Grade A, Large, Egg Yolk": "egg yolk",
    "Greek Yogurt Plain": "greek yogurt",
    "Milk": "milk glass",
    "Milk, Lowfat, Fluid, 1% Milkfat, With Added Vitamin A And Vitamin D": "milk",
    "Milk, Nonfat, Fluid, With Added Vitamin A And Vitamin D (Fat Free Or Skim)": "skim milk",
    "Milk, Reduced Fat, Fluid, 2% Milkfat, With Added Vitamin A And Vitamin D": "milk",
    "Milk, Whole, 3.25% Milkfat, With Added Vitamin D": "whole milk",
    "Yogurt": "yogurt",
    "Yogurt, Greek, Plain, Nonfat": "greek yogurt",
    "Yogurt, Greek, Strawberry, Nonfat": "strawberry yogurt",
    "Bacon Cooked": "bacon",
    "Beef Sticks": "beef jerky",
    "Chicken Burger": "chicken burger",
    "Chicken Curry": "chicken curry",
    "Chicken Popcorn": "popcorn chicken",
    "Chicken Sandwich": "chicken sandwich",
    "Chicken Strips": "chicken strips",
    "Chicken, Broiler Or Fryers, Breast, Skinless, Boneless, Meat Only, Cooked, Braised": "grilled chicken breast",
    "Chicken, Broilers Or Fryers, Drumstick, Meat Only, Cooked, Braised": "chicken drumstick",
    "Fish, Haddock, Raw": "haddock fish",
    "Fish, Pollock, Raw": "fish fillet",
    "Fish, Tuna, Light, Canned In Water, Drained Solids": "canned tuna",
    "Fried Shrimp": "fried shrimp",
    "Goat Meat": "goat meat",
    "Nuts, Almonds, Dry Roasted, With Salt Added": "roasted almonds",
    "Oyster Cooked": "cooked oyster",
    "Pork Cooked": "pork",
    "Protein Powder": "protein shake",
    "Rabbit Meat": "rabbit stew",
    "Salmon": "salmon fillet",
    "Steak Fries": "steak and fries",
    "Tuna Fish": "tuna steak",
    "Tuna Salad": "tuna salad",
    "Turkey Cooked": "roast turkey",
    "Turkey, Ground, 93% Lean, 7% Fat, Pan-Broiled Crumbles": "ground turkey",
    "Cashew Nuts": "cashew nuts",
    "Chia Seeds": "chia seeds",
    "Honey": "honey",
    "Peanut Butter, Smooth Style, With Salt": "peanut butter",
    "Seeds, Sunflower Seed Kernels, Dry Roasted, With Salt Added": "sunflower seeds",
    "Brownie": "chocolate brownie",
    "Cheese Burger": "cheeseburger",
    "Cheese Pizza": "cheese pizza",
    "Chocolate Doughnuts": "chocolate donut",
    "Chocolate Icecream": "chocolate ice cream",
    "Dark Chocolates": "dark chocolate",
    "Grapefruit Juice, White, Canned Or Bottled, Unsweetened": "grapefruit juice",
    "Macroni N Cheese": "mac and cheese",
    "Marshmallows": "marshmallow",
    "Nachos": "nachos",
    "Peproni Pizza": "pepperoni pizza",
    "Pop Corn": "popcorn",
    "Pop Corn - Caramel": "caramel popcorn",
    "Rice Pudding": "rice pudding",
    "Spaghetti And Meatballs": "spaghetti meatballs",
    "Strawberry Icecream": "strawberry ice cream",
    "Sugar Doughnuts": "sugar donut",
    "Vanilla Ice Cream": "vanilla ice cream",
    "Coffee": "coffee cup",
    "Green Tea": "green tea",
    "Tea": "tea cup",
    "Peaches, Yellow, Raw": "peach fruit",
}


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def build_query_variants(food_name: str) -> list[str]:
    raw_name = (food_name or "").strip()
    if not raw_name:
        return []

    variants = [raw_name]

    without_parentheses = re.sub(r"\s*\([^)]*\)", "", raw_name).strip()
    if without_parentheses:
        variants.append(without_parentheses)

    first_comma_part = raw_name.split(",")[0].strip()
    if first_comma_part:
        variants.append(first_comma_part)

    comma_parts = [part.strip() for part in raw_name.split(",") if part.strip()]
    if len(comma_parts) >= 2:
        descriptor_first = f"{comma_parts[1]} {comma_parts[0]}".strip()
        if descriptor_first:
            variants.append(descriptor_first)

    cleaned = raw_name
    cleaned = re.sub(r"\([^)]*\)", " ", cleaned)
    cleaned = re.sub(
        r"\b(raw|cooked|frozen|canned|prepared|drained|with added vitamins?|with skin|lowfat|low fat|low moisture|part skim|part-skim|restaurant|commercial|instant|instantaneous|ready to eat|ready-to-eat|unsweetened|sweetened|plain|large|small|medium|dry roasted|boiled|baked|fried|fresh)\b",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"[,/\-]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if cleaned:
        variants.append(cleaned)

    if first_comma_part:
        singularized = re.sub(r"\b([A-Za-z]+)s\b$", r"\1", first_comma_part)
        if singularized and singularized != first_comma_part:
            variants.append(singularized)

    return list(dict.fromkeys(variant for variant in variants if variant))


def build_local_image_index() -> dict[str, str]:
    index: dict[str, str] = {}
    for folder in [BASE_DIR / "static" / "images" / "food", BASE_DIR / "static" / "images"]:
        if not folder.exists():
            continue
        for file_path in folder.iterdir():
            if not file_path.is_file() or file_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
                continue
            normalized = normalize_key(file_path.stem)
            index.setdefault(normalized, f"/static/images/{'food/' if file_path.parent.name == 'food' else ''}{file_path.name}")
    return index


LOCAL_IMAGE_INDEX = build_local_image_index()


def fetch_themealdb(keyword: str) -> str | None:
    try:
        response = requests.get(
            "https://www.themealdb.com/api/json/v1/1/search.php",
            params={"s": keyword},
            timeout=8,
        )
        data = response.json()
        meals = data.get("meals")
        if meals:
            return meals[0]["strMealThumb"]
    except Exception:
        return None
    return None


def fetch_spoonacular_recipe(keyword: str) -> str | None:
    if not SPOONACULAR_KEY:
        return None
    try:
        response = requests.get(
            "https://api.spoonacular.com/recipes/complexSearch",
            params={"query": keyword, "number": 1, "apiKey": SPOONACULAR_KEY},
            timeout=8,
        )
        data = response.json()
        results = data.get("results", [])
        if results and results[0].get("image"):
            return results[0]["image"]
    except Exception:
        return None
    return None


def fetch_spoonacular_ingredient(keyword: str) -> str | None:
    if not SPOONACULAR_KEY:
        return None
    try:
        response = requests.get(
            "https://api.spoonacular.com/food/ingredients/search",
            params={"query": keyword, "number": 1, "apiKey": SPOONACULAR_KEY},
            timeout=8,
        )
        data = response.json()
        results = data.get("results", [])
        if results and results[0].get("image"):
            return f"https://spoonacular.com/cdn/ingredients_250x250/{results[0]['image']}"
    except Exception:
        return None
    return None


def fetch_local_image(food_name: str) -> str | None:
    for query in build_query_variants(food_name):
        image_url = LOCAL_IMAGE_INDEX.get(normalize_key(query))
        if image_url:
            return image_url
    return None


def fetch_best_image(food_name: str) -> tuple[str | None, str]:
    local_image = fetch_local_image(food_name)
    if local_image:
        return local_image, "local"

    for query in build_query_variants(food_name):
        image_url = fetch_themealdb(query)
        if image_url:
            return image_url, "MealDB"
        time.sleep(DELAY)

        image_url = fetch_spoonacular_recipe(query)
        if image_url:
            return image_url, "Spoonacular-dish"
        time.sleep(DELAY)

        image_url = fetch_spoonacular_ingredient(query)
        if image_url:
            return image_url, "Spoonacular-ingr"
        time.sleep(DELAY)

    return None, ""


def load_input_csv() -> Path:
    if INPUT_CSV.exists():
        return INPUT_CSV
    if FALLBACK_INPUT_CSV.exists():
        return FALLBACK_INPUT_CSV
    raise FileNotFoundError(
        f"Could not find food_master.csv next to this script or at {FALLBACK_INPUT_CSV}"
    )


def main() -> None:
    input_csv = load_input_csv()
    df = pd.read_csv(input_csv)

    name_column = "Food_items" if "Food_items" in df.columns else "name"
    if "imagepath" not in df.columns:
        df["imagepath"] = ""
    df["imagepath"] = df["imagepath"].fillna("")

    cache: dict[str, str] = {}
    if CACHE_FILE.exists():
        with CACHE_FILE.open("r", encoding="utf-8") as cache_file:
            cache = json.load(cache_file)

    found = 0
    not_found: list[tuple[str, str]] = []

    for idx, row in df.iterrows():
        food_name = str(row[name_column]).strip()
        if not food_name:
            continue

        existing_image = str(row.get("imagepath", "")).strip()
        if existing_image.startswith("http") or existing_image.startswith("/"):
            found += 1
            continue

        if food_name in cache:
            df.at[idx, "imagepath"] = cache[food_name]
            print(f"[cache] {food_name}")
            found += 1
            continue

        keyword = KEYWORD_MAP.get(food_name)
        if not keyword:
            keyword = build_query_variants(food_name)[0].lower()

        image_url, source = fetch_best_image(food_name)
        if image_url:
            df.at[idx, "imagepath"] = image_url
            cache[food_name] = image_url
            print(f"[✓ {source:<17}] {food_name} -> {image_url}")
            found += 1
        else:
            not_found.append((food_name, keyword))
            print(f"[✗ not found       ] {food_name} (tried: {keyword})")

        if idx % 25 == 0:
            with CACHE_FILE.open("w", encoding="utf-8") as cache_file:
                json.dump(cache, cache_file, indent=2)

    with CACHE_FILE.open("w", encoding="utf-8") as cache_file:
        json.dump(cache, cache_file, indent=2)

    df.to_csv(OUTPUT_CSV, index=False)

    total = len(df)
    print(f"\n{'─' * 65}")
    print(f"Total     : {total}")
    print(f"Found     : {found}")
    print(f"Missing   : {len(not_found)}")
    print(f"Output    : {OUTPUT_CSV}")


if __name__ == "__main__":
    main()