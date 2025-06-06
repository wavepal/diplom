# Generated by Django 4.2.7 on 2025-05-10 16:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0020_remove_medcentergroup_centers_regionmedcenter_group_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='medcentergroup',
            options={},
        ),
        migrations.RemoveField(
            model_name='medcentergroup',
            name='updated_at',
        ),
        migrations.AlterField(
            model_name='regionmedcenter',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='med_centers', to='index.medcentergroup'),
        ),
    ]
