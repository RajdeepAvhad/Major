from django.core.management.base import BaseCommand

from recommender.models import Food


GI_DATA = {
    "White Rice": 72, "Brown Rice": 50, "Basmati Rice Cooked": 58,
    "Roti Wheat": 62, "Chappati": 62, "Dosa": 77, "Idli": 70,
    "Poha": 70, "Upma": 65, "Khichdi": 55,
    "Bananas": 51, "Apples": 36, "Grapes": 59, "Orange": 43,
    "Strawberries": 40, "Pears": 38,
    "Dal Cooked": 29, "Rajma Cooked": 24, "Chole Cooked": 28,
    "Lentils": 32, "Peas": 51, "Beans": 30,
    "Oat Bran Cooked": 55, "Cereals-Corn Flakes": 81,
    "French Fries": 75, "Boiled Potatoes": 78, "Sweet Potatoes Cooked": 61,
    "Yogurt": 36, "Greek Yogurt Plain": 11, "Milk": 31,
    "Chicken Curry": 0, "Salmon": 0, "Tuna Fish": 0, "Eggs, Grade A, Large, Egg Whole": 0,
    "Paneer": 0, "Palak Paneer": 15, "Dal Makhani": 29,
    "Corn": 60, "Mushrooms": 15, "Cauliflower": 15, "Brocolli": 10,
    "Honey": 61, "Dark Chocolates": 23, "Chocolate Icecream": 61,
    "Peanut Butter, Smooth Style, With Salt": 14,
    "Cashew Nuts": 22, "Almonds": 0, "Chia Seeds": 1,
    "Cheese Pizza": 80, "Cheese Burger": 66, "Nachos": 74,
    "Noodles": 40, "Pasta Canned With Tomato Sauce": 45,
    "American Cheese": 0, "American cheese": 0,
    "Cheese, American, Restaurant": 0,
    "Cheese, Cheddar": 0,
    "Cheese, Cottage, Lowfat, 2% Milkfat": 60,
    "Cheese, Dry White, Queso Seco": 0,
    "Cheese, Mozzarella, Low Moisture, Part-Skim": 0,
    "Cheese, Parmesan, Grated": 0,
    "Cheese, Pasteurized Process, American, Vitamin D F": 0,
    "Cheese, Ricotta, Whole Milk": 0,
    "Cheese, Swiss": 0,
    "Cottage Cheese With Vegetables": 60,
    "Cottage cheese with vegetables": 60,
    "Egg Yolk Cooked": 0, "Egg Yolk cooked": 0,
    "Egg, White, Dried": 0,
    "Egg, White, Raw, Frozen, Pasteurized": 0,
    "Egg, Whole, Dried": 0,
    "Egg, Whole, Raw, Frozen, Pasteurized": 0,
    "Egg, Yolk, Dried": 0,
    "Egg, Yolk, Raw, Frozen, Pasteurized": 0,
    "Eggs, Grade A, Large, Egg White": 0,
    "Eggs, Grade A, Large, Egg Yolk": 0,
    "Flour, Bread, White, Enriched, Unbleached": 70,
    "Flour, Corn, Yellow, Fine Meal, Enriched": 72,
    "Flour, Pastry, Unenriched, Unbleached": 47,
    "Flour, Rice, Brown": 50,
    "Flour, Rice, Glutinous": 65,
    "Flour, Rice, White, Unenriched": 81,
    "Flour, Soy, Defatted": 50,
    "Flour, Soy, Full-Fat": 36,
    "Flour, Wheat, All-Purpose, Enriched, Bleached": 70,
    "Flour, Wheat, All-Purpose, Enriched, Unbleached": 70,
    "Flour, Wheat, All-Purpose, Unenriched, Unbleached": 70,
    "Flour, Whole Wheat, Unenriched": 54,
}


def gi_category(value):
    if value is None:
        return None
    if value < 55:
        return "Low"
    if value < 70:
        return "Medium"
    return "High"


class Command(BaseCommand):
    help = "Seed glycemic index values for foods"

    def handle(self, *args, **options):
        updated = 0

        for name, gi_value in GI_DATA.items():
            updated += Food.objects.filter(name=name).update(
                glycemic_index=gi_value,
                gi_category=gi_category(gi_value),
            )

        self.stdout.write(f"Updated {updated} foods")