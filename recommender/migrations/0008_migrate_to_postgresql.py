# Generated migration for PostgreSQL migration

from django.db import migrations, models
from django.utils import timezone
import json


def convert_textfield_to_json(apps, schema_editor):
    """
    Convert existing TextField JSON strings to proper JSON data.
    This is a data migration to handle the TextField -> JSONField conversion.
    """
    SavedDiet = apps.get_model('recommender', 'SavedDiet')
    
    for diet in SavedDiet.objects.all():
        if isinstance(diet.selected_items, str):
            try:
                # Parse the JSON string and save it back
                diet.selected_items = json.loads(diet.selected_items)
                diet.save(update_fields=['selected_items'])
            except (json.JSONDecodeError, TypeError):
                # If parsing fails, set to empty list
                diet.selected_items = []
                diet.save(update_fields=['selected_items'])


def convert_json_to_textfield(apps, schema_editor):
    """
    Reverse migration: Convert JSON back to TextField string.
    """
    SavedDiet = apps.get_model('recommender', 'SavedDiet')
    
    for diet in SavedDiet.objects.all():
        if isinstance(diet.selected_items, (list, dict)):
            diet.selected_items = json.dumps(diet.selected_items)
            diet.save(update_fields=['selected_items'])


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0007_preferences_favorites_water'),
    ]

    operations = [
        # Step 1: Change SavedDiet.selected_items from TextField to JSONField
        migrations.AlterField(
            model_name='saveddiet',
            name='selected_items',
            field=models.JSONField(blank=True, default=list),
        ),
        
        # Step 2: Run data migration to convert existing data
        migrations.RunPython(
            convert_textfield_to_json,
            reverse_code=convert_json_to_textfield,
        ),
        
        # Step 3: Add database index to WaterLog.log_date
        migrations.AlterField(
            model_name='waterlog',
            name='log_date',
            field=models.DateField(db_index=True, default=timezone.localdate),
        ),
        
        # Step 4: Add indexes to SavedDiet for better query performance
        migrations.AddIndex(
            model_name='saveddiet',
            index=models.Index(fields=['-created_at'], name='recommender_created_idx'),
        ),
        migrations.AddIndex(
            model_name='saveddiet',
            index=models.Index(fields=['user', 'period'], name='recommender_user_period_idx'),
        ),
        migrations.AddIndex(
            model_name='saveddiet',
            index=models.Index(fields=['session_key', 'period'], name='recommender_session_period_idx'),
        ),
        
        # Step 5: Add indexes to FavoriteFood
        migrations.AddIndex(
            model_name='favoritefood',
            index=models.Index(fields=['user', 'food'], name='recommender_user_food_idx'),
        ),
        migrations.AddIndex(
            model_name='favoritefood',
            index=models.Index(fields=['session_key', 'food'], name='recommender_session_food_idx'),
        ),
        
        # Step 6: Add indexes to WaterLog
        migrations.AddIndex(
            model_name='waterlog',
            index=models.Index(fields=['user', 'log_date'], name='recommender_user_logdate_idx'),
        ),
        migrations.AddIndex(
            model_name='waterlog',
            index=models.Index(fields=['session_key', 'log_date'], name='recommender_session_logdate_idx'),
        ),
    ]
