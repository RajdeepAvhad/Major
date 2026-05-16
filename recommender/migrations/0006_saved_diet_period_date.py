from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("recommender", "0005_alter_food_id_alter_userlist_id_saveddiet"),
    ]

    operations = [
        migrations.AddField(
            model_name="saveddiet",
            name="period",
            field=models.CharField(default="daily", max_length=10),
        ),
        migrations.AddField(
            model_name="saveddiet",
            name="plan_date",
            field=models.DateField(blank=True, default=django.utils.timezone.localdate, null=True),
        ),
    ]
