# Generated by Django 4.2.7 on 2024-07-30 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0013_alter_usercity_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='responses',
            name='authenticated_responder',
            field=models.BooleanField(default=False),
        ),
    ]
