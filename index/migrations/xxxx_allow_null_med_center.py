from django.db import migrations, models

def set_default_med_center(apps, schema_editor):
    UserMed = apps.get_model('index', 'UserMed')
    # Установим пустую строку для существующих записей
    UserMed.objects.filter(med_center__isnull=True).update(med_center='')

class Migration(migrations.Migration):

    dependencies = [
        ('index', 'XXXX_add_region_med_centers'),  # Замените на имя вашей последней миграции
    ]

    operations = [
        # Сначала установим значение по умолчанию для существующих записей
        migrations.RunPython(set_default_med_center),
        
        # Затем изменим поле, чтобы оно принимало null значения
        migrations.AlterField(
            model_name='usermed',
            name='med_center',
            field=models.CharField(max_length=50, blank=True, null=True),
        ),
    ] 