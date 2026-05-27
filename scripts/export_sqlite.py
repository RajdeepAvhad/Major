#!/usr/bin/env python
"""
Export SQLite data to JSON fixtures for migration to PostgreSQL.

This script exports all data from the SQLite database to a JSON file
that can be loaded into the new PostgreSQL database.

Usage:
    python scripts/export_sqlite.py
"""

import os
import sys
import json
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodrec.settings')

# Ensure we're using SQLite (not PostgreSQL)
os.environ.pop('DATABASE_URL', None)

import django
django.setup()

from django.core.management import call_command
from django.db import connection


def export_data():
    """Export all data from SQLite to JSON fixtures."""
    
    print("=" * 70)
    print("EatRight Database Export - SQLite to JSON")
    print("=" * 70)
    
    # Ensure we're connected to SQLite
    db_engine = connection.settings_dict['ENGINE']
    print(f"\n✓ Database engine: {db_engine}")
    
    if 'sqlite' not in db_engine:
        print("\n❌ ERROR: This script must be run with SQLite database!")
        print("   Make sure DATABASE_URL is not set in your environment.")
        sys.exit(1)
    
    # Create fixtures directory if it doesn't exist
    fixtures_dir = project_root / 'fixtures'
    fixtures_dir.mkdir(exist_ok=True)
    
    output_file = fixtures_dir / 'initial_data.json'
    
    print(f"\n📦 Exporting data to: {output_file}")
    print("\nExporting models:")
    print("  - auth.User")
    print("  - recommender.Food")
    print("  - recommender.UserList")
    print("  - recommender.SavedDiet")
    print("  - recommender.UserPreference")
    print("  - recommender.FavoriteFood")
    print("  - recommender.WaterLog")
    
    # Export data using Django's dumpdata command
    # Exclude contenttypes and sessions as they'll be recreated
    with open(output_file, 'w', encoding='utf-8') as f:
        call_command(
            'dumpdata',
            'auth.User',
            'recommender.Food',
            'recommender.UserList',
            'recommender.SavedDiet',
            'recommender.UserPreference',
            'recommender.FavoriteFood',
            'recommender.WaterLog',
            indent=2,
            stdout=f,
            natural_foreign=True,
            natural_primary=True,
        )
    
    # Get file size
    file_size = output_file.stat().st_size
    file_size_kb = file_size / 1024
    
    print(f"\n✅ Export completed successfully!")
    print(f"   File size: {file_size_kb:.2f} KB")
    print(f"   Location: {output_file}")
    
    # Parse and show statistics
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Count records by model
    model_counts = {}
    for record in data:
        model = record.get('model', 'unknown')
        model_counts[model] = model_counts.get(model, 0) + 1
    
    print("\n📊 Exported records:")
    for model, count in sorted(model_counts.items()):
        print(f"   {model}: {count} records")
    
    print(f"\n   Total: {len(data)} records")
    
    print("\n" + "=" * 70)
    print("Next steps:")
    print("=" * 70)
    print("1. Set DATABASE_URL in your .env file (NeonDB connection string)")
    print("2. Install PostgreSQL dependencies: pip install -r requirements.txt")
    print("3. Run migrations: python manage.py migrate")
    print("4. Load data: python manage.py load_initial_data")
    print("5. Verify data: python manage.py shell")
    print("=" * 70)


if __name__ == '__main__':
    try:
        export_data()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
