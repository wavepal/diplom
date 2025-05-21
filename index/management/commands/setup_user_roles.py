from django.core.management.base import BaseCommand
from index.models import User, UserRole

class Command(BaseCommand):
    help = 'Устанавливает роли для всех пользователей: admin получает роль админа, все остальные - роль пользователя'

    def handle(self, *args, **options):
        # Установка роли админа для пользователя admin
        try:
            admin_user = User.objects.get(username='admin')
            admin_role, created = UserRole.objects.get_or_create(user=admin_user)
            admin_role.role = UserRole.ADMIN
            admin_role.save()
            
            # Обновляем права суперпользователя
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.save()
            
            self.stdout.write(self.style.SUCCESS(f'Пользователю {admin_user.username} установлена роль администратора'))
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('Пользователь admin не найден'))

        # Установка роли пользователя для всех остальных
        users = User.objects.exclude(username='admin')
        for user in users:
            user_role, created = UserRole.objects.get_or_create(user=user)
            user_role.role = UserRole.USER
            user_role.save()
            
            # Сбрасываем права суперпользователя
            user.is_superuser = False
            user.is_staff = False
            user.save()
            
        self.stdout.write(self.style.SUCCESS(f'Установлена роль пользователя для {users.count()} пользователей')) 