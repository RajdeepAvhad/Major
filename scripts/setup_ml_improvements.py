"""
Quick Setup Script for ML Improvements
Automates the entire setup process
"""

import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def run_command(description, command):
    """Run a command and report status"""
    print(f"▶ {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"  ✓ Success")
            if result.stdout:
                print(f"  Output: {result.stdout[:200]}")
            return True
        else:
            print(f"  ✗ Failed")
            if result.stderr:
                print(f"  Error: {result.stderr[:200]}")
            return False
    
    except Exception as e:
        print(f"  ✗ Exception: {e}")
        return False


def check_file_exists(filepath, description):
    """Check if a file exists"""
    if filepath.exists():
        size_kb = filepath.stat().st_size / 1024
        print(f"  ✓ {description}: {filepath.name} ({size_kb:.1f} KB)")
        return True
    else:
        print(f"  ✗ {description}: {filepath.name} not found")
        return False


def main():
    """Main setup function"""
    print_header("EatRight ML Improvements - Quick Setup")
    
    print("This script will:")
    print("  1. Install required dependencies")
    print("  2. Fetch USDA foods (500+ items)")
    print("  3. Merge datasets")
    print("  4. Run database migrations")
    print("  5. Evaluate model performance")
    print("\nEstimated time: 10-15 minutes")
    
    input("\nPress Enter to continue or Ctrl+C to cancel...")
    
    # Step 1: Install dependencies
    print_header("Step 1: Installing Dependencies")
    success = run_command(
        "Installing imbalanced-learn",
        "pip install imbalanced-learn>=0.12"
    )
    
    if not success:
        print("\n⚠ Warning: Dependency installation failed. Continuing anyway...")
    
    # Step 2: Parse USDA local CSV
    print_header("Step 2: Parsing USDA Local CSV")
    
    # Check if USDA CSV exists
    usda_csv = BASE_DIR / 'static' / 'data' / 'FoodData_Central_foundation_food.csv'
    if not usda_csv.exists():
        print("⚠ USDA CSV file not found!")
        print(f"Expected location: {usda_csv}")
        print("\nPlease download the file:")
        print("1. Visit: https://fdc.nal.usda.gov/download-datasets.html")
        print("2. Download 'Foundation Foods' CSV")
        print("3. Place in: static/data/")
        print("\nSee USDA_DOWNLOAD_GUIDE.md for detailed instructions")
        print("\nContinuing with existing data...")
    else:
        print("✓ USDA CSV file found")
        
        success = run_command(
            "Parsing USDA local CSV",
            "python scripts/parse_usda_local.py"
        )
        
        if not success:
            print("\n⚠ Warning: USDA parsing failed.")
            print("Continuing with existing data...")
    
    # Check if food_expanded.csv was created
    expanded_file = BASE_DIR / 'static' / 'data' / 'food_expanded.csv'
    if expanded_file.exists():
        check_file_exists(expanded_file, "USDA foods dataset")
    else:
        print("⚠ food_expanded.csv not created. Will use existing food.csv only.")
    
    # Step 3: Merge datasets
    print_header("Step 3: Merging Datasets")
    
    success = run_command(
        "Merging food.csv + food_expanded.csv + indian_foods.csv",
        "python scripts/merge_datasets.py"
    )
    
    if not success:
        print("\n✗ Error: Dataset merge failed!")
        return
    
    # Check if food_master.csv was created
    master_file = BASE_DIR / 'static' / 'data' / 'food_master.csv'
    if not check_file_exists(master_file, "Master dataset"):
        print("\n✗ Error: food_master.csv not created!")
        return
    
    # Step 4: Run migrations
    print_header("Step 4: Running Database Migrations")
    
    success = run_command(
        "Applying Food model migrations",
        "python manage.py migrate"
    )
    
    if not success:
        print("\n⚠ Warning: Migration failed. You may need to run it manually.")
    
    # Step 5: Evaluate model
    print_header("Step 5: Evaluating Model Performance")
    
    success = run_command(
        "Running 5-fold cross-validation",
        "python scripts/evaluate_model.py"
    )
    
    if not success:
        print("\n⚠ Warning: Model evaluation failed. You can run it manually later.")
    
    # Check if evaluation results were created
    eval_file = BASE_DIR / 'static' / 'data' / 'model_eval.json'
    check_file_exists(eval_file, "Model evaluation results")
    
    # Final summary
    print_header("Setup Complete!")
    
    print("✓ Files created:")
    files_to_check = [
        ('static/data/indian_foods.csv', 'Indian foods dataset'),
        ('static/data/food_expanded.csv', 'USDA foods dataset'),
        ('static/data/food_master.csv', 'Master merged dataset'),
        ('static/data/model_eval.json', 'Model evaluation results'),
        ('recommender/migrations/0009_add_food_metadata_fields.py', 'Food model migration'),
    ]
    
    for filepath, description in files_to_check:
        full_path = BASE_DIR / filepath
        check_file_exists(full_path, description)
    
    print("\n✓ Next steps:")
    print("  1. Restart Django server: python manage.py runserver")
    print("  2. Test recommendations with different user profiles")
    print("  3. Check model_eval.json for performance metrics")
    print("  4. Read ML_IMPROVEMENTS_README.md for full documentation")
    
    print("\n" + "=" * 70)
    print("  Setup completed successfully! 🎉")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Setup failed with error: {e}")
        sys.exit(1)
