from django.db import migrations

def add_region_med_centers(apps, schema_editor):
    RegionMedCenter = apps.get_model('index', 'RegionMedCenter')
    
    data = [
        # Астана
        ('ASTANA', 'ТОО «Медикер Астана»', 'Коргалжинское шоссе, 4/1'),
        ('ASTANA', 'ТОО «Медикер Педиатрия»', 'ул.Ташенова, 20'),
        ('ASTANA', 'ТОО «Медикер Илек»', 'пр.Кабанбай батыра, 17'),
        
        # Алматы
        ('ALMATY', 'ТОО «Алатау Ассистанс»', 'ул.Навои, 310'),
        ('ALMATY', 'ТОО «Qamqor Clinic Almaty»', 'ул.Сатпаева, 18а'),
        ('ALMATY', 'ТОО «MIH»', 'ул.Азербаева, 67'),
        
        # Актюбинская область
        ('AKTOBE', 'ТОО «Медикер Илек»', 'мкр. Алтын Орда, кв. Мәңгілік Ел 21, корпус 1'),
        
        # Атырауская область
        ('ATYRAUSKAYA', 'ТОО «Медикер Жайык»', 'ул.Севастополь, 10А'),
        
        # Западно-Казахстанская область
        ('ZAPADNO', 'ТОО «Медикер Аксай»', 'мкр.2, дом 1/3'),
        ('ZAPADNO', 'ТОО «Медикер ЮК»', 'ул.Курмангазы, д.196'),
        
        # Кызылординская область
        ('KYZYLORDA', 'ТОО «МЦ Онидрис»', 'ул.Ауезова, 9'),
        
        # Мангистауская область
        ('MANGISTAU', 'ТОО «Медикер Каспий»', '26 мкр., 17/1'),
        ('MANGISTAU', 'ТОО «Uzenmedics»', 'Жанаозен, мкр.Самал, 39А'),
        
        # Павлодарская область
        ('PAVLODAR', 'ТОО «Медикер Ертис»', 'ул.Павлова, 38/1'),
        
        # Южно-Казахстанская область
        ('TURKESTAN', 'ТОО «Медикер ЮК»', 'ул.Аргынбекова, 640А'),
        ('TURKESTAN', 'ТОО «Мейирим»', 'ул.Бейбитшилик, 2Б'),
    ]
    
    for region, med_center, address in data:
        RegionMedCenter.objects.create(
            region=region,
            med_center=med_center,
            address=address
        )

class Migration(migrations.Migration):
    dependencies = [
        ('index', '0040_regionmedcenter'),  # Changed from 'previous_migration' to actual migration name
    ]

    operations = [
        migrations.RunPython(add_region_med_centers),
    ]