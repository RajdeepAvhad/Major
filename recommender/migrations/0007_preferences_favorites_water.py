from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("recommender", "0006_saved_diet_period_date"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserPreference",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("session_key", models.CharField(blank=True, default="", max_length=100)),
                ("age", models.IntegerField(blank=True, null=True)),
                ("weight", models.IntegerField(blank=True, null=True)),
                ("height", models.IntegerField(blank=True, null=True)),
                ("bodyfat", models.FloatField(blank=True, null=True)),
                ("goal", models.CharField(default="healthy", max_length=20)),
                ("activity", models.CharField(default="Heavy", max_length=20)),
                ("gender", models.CharField(default="", max_length=10)),
                ("category", models.CharField(default="none", max_length=20)),
                ("plan_period", models.CharField(default="daily", max_length=10)),
                ("plan_date", models.DateField(blank=True, default=django.utils.timezone.localdate, null=True)),
                ("reminder_time", models.CharField(blank=True, default="", max_length=5)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="auth.user")),
            ],
            options={
                "ordering": ["-updated_at"],
            },
        ),
        migrations.CreateModel(
            name="FavoriteFood",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("session_key", models.CharField(blank=True, default="", max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("food", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="recommender.food")),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="auth.user")),
            ],
            options={
                "ordering": ["-created_at"],
                "unique_together": {("user", "session_key", "food")},
            },
        ),
        migrations.CreateModel(
            name="WaterLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("session_key", models.CharField(blank=True, default="", max_length=100)),
                ("log_date", models.DateField(default=django.utils.timezone.localdate)),
                ("amount_ml", models.IntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="auth.user")),
            ],
            options={
                "ordering": ["-log_date"],
                "unique_together": {("user", "session_key", "log_date")},
            },
        ),
    ]
