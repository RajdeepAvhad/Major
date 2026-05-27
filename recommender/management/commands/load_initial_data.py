"""
Django management command to load initial data from fixtures.

This command loads the exported SQLite data into the new PostgreSQL database.

Usage:
    python manage.py load_initial_data
    python manage.py load_initial_data --file fixtures/custom_data.json
"""

import json
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import connection, transaction
from django.contrib.auth.models import User
from recommender.models import Food, UserList, SavedDiet, UserPreference, FavoriteFood, WaterLog


class Command(BaseCommand):
    help = 'Load initial data from JSON fixtures into PostgreSQL database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='fixtures/initial_data.json',
            help='Path to the JSON fixture file (default: fixtures/initial_data.json)',
        )
        parser.add_argument(
            '--skip-confirmation',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        fixture_file = Path(options['file'])
        skip_confirmation = options['skip_confirmation']

        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("EatRight Database Import - Load Initial Data"))
        self.stdout.write("=" * 70)

        # Check database engine
        db_engine = connection.settings_dict['ENGINE']
        self.stdout.write(f"\n✓ Database engine: {db_engine}")

        if 'postgresql' not in db_engine:
            self.stdout.write(self.style.WARNING(
                "\n⚠️  WARNING: You're not using PostgreSQL!"
            ))
            self.stdout.write(
                "   This command is designed for PostgreSQL migration."
            )
            self.stdout.write(
                "   Set DATABASE_URL in your .env file to use NeonDB.\n"
            )

        # Check if fixture file exists
        if not fixture_file.exists():
            raise CommandError(
                f"Fixture file not found: {fixture_file}\n"
                f"Run 'python scripts/export_sqlite.py' first to export data."
            )

        # Get file info
        file_size = fixture_file.stat().st_size / 1024
        self.stdout.write(f"\n📦 Fixture file: {fixture_file}")
        self.stdout.write(f"   Size: {file_size:.2f} KB")

        # Parse fixture to show statistics
        with open(fixture_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        model_counts = {}
        for record in data:
            model = record.get('model', 'unknown')
            model_counts[model] = model_counts.get(model, 0) + 1

        self.stdout.write("\n📊 Records to import:")
        for model, count in sorted(model_counts.items()):
            self.stdout.write(f"   {model}: {count} records")
        self.stdout.write(f"\n   Total: {len(data)} records")

        # Check current database state
        self.stdout.write("\n📋 Current database state:")
        current_counts = {
            'auth.user': User.objects.count(),
            'recommender.food': Food.objects.count(),
            'recommender.userlist': UserList.objects.count(),
            'recommender.saveddiet': SavedDiet.objects.count(),
            'recommender.userpreference': UserPreference.objects.count(),
            'recommender.favoritefood': FavoriteFood.objects.count(),
            'recommender.waterlog': WaterLog.objects.count(),
        }

        for model, count in current_counts.items():
            status = "✓ Empty" if count == 0 else f"⚠️  {count} existing records"
            self.stdout.write(f"   {model}: {status}")

        # Confirmation prompt
        if not skip_confirmation:
            self.stdout.write("\n" + "=" * 70)
            self.stdout.write(self.style.WARNING("⚠️  WARNING: This will load data into the database!"))
            self.stdout.write("=" * 70)
            
            if any(count > 0 for count in current_counts.values()):
                self.stdout.write(self.style.ERROR(
                    "\n⚠️  Database is not empty! Existing data may conflict."
                ))
                self.stdout.write(
                    "   Consider backing up or clearing the database first.\n"
                )

            confirm = input("\nDo you want to continue? [y/N]: ")
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING("\n❌ Import cancelled."))
                return

        # Load data
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write("Loading data...")
        self.stdout.write("=" * 70 + "\n")

        try:
            with transaction.atomic():
                # Use Django's loaddata command
                call_command('loaddata', str(fixture_file), verbosity=2)

            self.stdout.write("\n" + "=" * 70)
            self.stdout.write(self.style.SUCCESS("✅ Data loaded successfully!"))
            self.stdout.write("=" * 70)

            # Show final counts
            self.stdout.write("\n📊 Final database state:")
            final_counts = {
                'auth.user': User.objects.count(),
                'recommender.food': Food.objects.count(),
                'recommender.userlist': UserList.objects.count(),
                'recommender.saveddiet': SavedDiet.objects.count(),
                'recommender.userpreference': UserPreference.objects.count(),
                'recommender.favoritefood': FavoriteFood.objects.count(),
                'recommender.waterlog': WaterLog.objects.count(),
            }

            for model, count in final_counts.items():
                self.stdout.write(f"   {model}: {count} records")

            self.stdout.write("\n" + "=" * 70)
            self.stdout.write("Next steps:")
            self.stdout.write("=" * 70)
            self.stdout.write("1. Verify data: python manage.py shell")
            self.stdout.write("2. Create superuser (if needed): python manage.py createsuperuser")
            self.stdout.write("3. Run server: python manage.py runserver")
            self.stdout.write("4. Test the application thoroughly")
            self.stdout.write("=" * 70 + "\n")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ ERROR: {e}"))
            raise CommandError(f"Failed to load data: {e}")
