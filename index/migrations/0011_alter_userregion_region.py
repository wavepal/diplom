# Generated by Django 4.2.7 on 2024-07-29 17:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0010_region_userregion_remove_user_city_delete_usercity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userregion',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_regions', to='index.region'),
        ),
    ]
