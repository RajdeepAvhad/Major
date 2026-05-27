# USDA Foundation Foods CSV - Download Guide

## 📥 Why Use Local CSV Instead of API?

The USDA API is geo-blocked for Indian IPs, returning 403 Forbidden errors. Instead, we'll use the pre-downloaded CSV file which contains the same data.

---

## 🔽 Download Instructions

### Step 1: Visit USDA Download Page

Go to:
```
https://fdc.nal.usda.gov/download-datasets.html
```

### Step 2: Find Foundation Foods

Scroll down to find **"Foundation Foods"** section.

### Step 3: Download CSV

Click on **"Download"** button for:
- **Foundation Foods CSV** (Full Download)
- File size: ~50-100 MB
- Format: ZIP file

### Step 4: Extract the ZIP

Extract the downloaded ZIP file. You'll find:
```
FoodData_Central_foundation_food_csv_YYYY-MM-DD/
├── food.csv
├── nutrient.csv
├── food_nutrient.csv
└── ... (other files)
```

### Step 5: Copy to Project

Copy the **entire folder** or just the main CSV file to:
```
C:\Users\Rajdeep\OneDrive\Desktop\Major\static\data\
```

**Expected file path:**
```
C:\Users\Rajdeep\OneDrive\Desktop\Major\static\data\FoodData_Central_foundation_food.csv
```

---

## 🎯 Alternative: Simplified CSV

If the full CSV is too large or complex, you can also download:

### Option A: Foundation Foods (Simplified)
- Smaller file size
- Pre-processed nutrients
- Easier to parse

### Option B: SR Legacy Foods
- Legacy USDA database
- Well-structured
- Good alternative

---

## ✅ Verify Download

After copying the file, run:

```bash
python scripts/parse_usda_local.py
```

**Expected output:**
```
USDA Local CSV Parser
============================================================
✓ Loaded CSV with XXXX rows
✓ Filtered: XXXX → XXX foods
✓ Extracted XXX valid food items
✓ Saved to: static/data/food_expanded.csv
```

---

## 🔍 What the Script Does

1. **Reads local CSV** - No API calls
2. **Filters categories**:
   - Vegetables and Vegetable Products
   - Fruits and Fruit Juices
   - Legumes and Legume Products
   - Poultry Products
   - Finfish and Shellfish Products
   - Dairy and Egg Products
   - Cereal Grains and Pasta
   - Nut and Seed Products

3. **Maps nutrients**:
   - Energy → Calories
   - Protein → Proteins
   - Total lipid (fat) → Fats
   - Carbohydrate by difference → Carbohydrates
   - Fiber → Fibre
   - Sugars total → Sugars
   - Calcium, Iron, Sodium, Potassium, Vitamin D

4. **Sets meal flags** based on food type
5. **Outputs** `food_expanded.csv` in EatRight format

---

## 🚨 Troubleshooting

### Issue: File not found
**Error**: `❌ ERROR: USDA CSV file not found`

**Solution**: 
- Check file path is correct
- Ensure file is named exactly: `FoodData_Central_foundation_food.csv`
- Place in: `static/data/` folder

### Issue: CSV format error
**Error**: `❌ Failed to load CSV`

**Solution**:
- Try re-downloading the file
- Check if file is corrupted
- Try different CSV file from USDA

### Issue: No foods extracted
**Error**: `❌ No valid foods extracted`

**Solution**:
- Check CSV has correct columns
- Verify CSV is not empty
- Try Foundation Foods instead of SR Legacy

---

## 📊 Expected Results

After successful parsing:
- **Input**: USDA CSV (thousands of foods)
- **Output**: `food_expanded.csv` (300-500 foods)
- **Format**: Same as `food.csv`
- **Ready**: For merging with existing data

---

## 🔄 Next Steps

After downloading and parsing:

```bash
# 1. Parse USDA local CSV
python scripts/parse_usda_local.py

# 2. Merge all datasets
python scripts/merge_datasets.py

# 3. Run migrations
python manage.py migrate

# 4. Evaluate model
python scripts/evaluate_model.py
```

---

## 📞 Need Help?

If you encounter issues:
1. Check file path is correct
2. Verify CSV file is not corrupted
3. Try re-downloading from USDA
4. Check the script output for specific errors

---

**Last Updated**: 2026-05-26  
**Status**: Ready to use (no API key needed) ✅
