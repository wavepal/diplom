from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
import os
from django.utils import timezone

# Choices for different fields
CITY_CHOICES = [
    ('ASTANA', 'Астана'),
    ('ALMATY', 'Алматы'),
    ('AKTOBE', 'Актюбинская область'),
    ('ATYRAUSKAYA', 'Атырауская область'),
    ('ZAPADNO', 'Западно-Казахстанская область'),
    ('KYZYLORDA', 'Кызылординская область'),
    ('MANGISTAU', 'Мангистауская область'),
    ('PAVLODAR', 'Павлодарская область'),
    ('TURKESTAN', 'Южно-Казахстанская область'),
]

GENDER_CHOICES = [
    ('M', 'Мужской'),
    ('F', 'Женский'),
    ('O', 'Другой'),
]

ROLE_CHOICES = [
    ('ADMIN', 'Администратор'),
    ('TRAINER', 'Тренер'),
    ('MANAGER', 'Руководитель'),
    ('USER', 'Пользователь'),
]

class Image(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def delete(self, *args, **kwargs):
        # Удаляем файл изображения при удалении объекта
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super(Image, self).delete(*args, **kwargs)

class MedCenterGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class RegionMedCenter(models.Model):
    region = models.CharField(max_length=50, choices=CITY_CHOICES)
    med_center = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    group = models.ForeignKey(MedCenterGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='med_centers')

    class Meta:
        unique_together = ('region', 'med_center')

    def __str__(self):
        return f"{self.get_region_display()} - {self.med_center}"

    @classmethod
    def get_med_centers_by_region(cls, region):
        return cls.objects.filter(region=region)

class User(AbstractUser):
    # Fields that were previously in separate models
    city = models.CharField(max_length=50, blank=True, null=True, choices=CITY_CHOICES)
    med_center = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    description = models.CharField(max_length=256, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='USER')
    
    # Для обратной совместимости (чтобы не сломать вьюхи)
    @property
    def city_info(self):
        """Compatibility property for old code that accessed UserCity through city_info relation"""
        return UserCityCompatibility(self)
    
    @property
    def med_info(self):
        """Compatibility property for old code that accessed UserMed through med_info relation"""
        return UserMedCompatibility(self)
    
    @property
    def date_info(self):
        """Compatibility property for old code that accessed DateOfBirth through date_info relation"""
        return DateOfBirthCompatibility(self)
    
    @property
    def gender_info(self):
        """Compatibility property for old code that accessed UserGender through gender_info relation"""
        return UserGenderCompatibility(self)
    
    @property
    def desc_info(self):
        """Compatibility property for old code that accessed UserDesc through desc_info relation"""
        return UserDescCompatibility(self)
    
    @property
    def role_info(self):
        """Compatibility property for old code that accessed UserRole through role_info relation"""
        return UserRoleCompatibility(self)
    
    def get_city_display(self):
        """Return the display name of the city"""
        city_dict = dict(CITY_CHOICES)
        return city_dict.get(self.city, self.city)
    
    def age(self):
        """Calculate age based on date of birth"""
        if not self.date_of_birth:
            return None
        today = datetime.now().date()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    def is_admin(self):
        return self.role == 'ADMIN'

    def is_trainer(self):
        return self.role == 'TRAINER'

    def is_manager(self):
        return self.role == 'MANAGER'

    def is_regular_user(self):
        return self.role == 'USER'


# Compatibility classes to maintain backward compatibility with views
class UserCityCompatibility:
    def __init__(self, user):
        self.user = user
        self.city = user.city
        self.id = user.id
    
    def get_city_display(self):
        return self.user.get_city_display()
    
    def save(self, *args, **kwargs):
        self.user.save()
    
    @classmethod
    def objects(cls):
        class Manager:
            @staticmethod
            def get_or_create(user):
                return UserCityCompatibility(user), False
            
            @staticmethod
            def create(user, city):
                user.city = city
                user.save()
                return UserCityCompatibility(user)
        
        return Manager()
    
    # Backward compatibility for CITY_CHOICES
    CITY_CHOICES = CITY_CHOICES

class UserMedCompatibility:
    def __init__(self, user):
        self.user = user
        self.med_center = user.med_center
        self.id = user.id
    
    def save(self, *args, **kwargs):
        self.user.save()
    
    @classmethod
    def objects(cls):
        class Manager:
            @staticmethod
            def get_or_create(user):
                return UserMedCompatibility(user), False
            
            @staticmethod
            def create(user, med_center):
                user.med_center = med_center
                user.save()
                return UserMedCompatibility(user)
            
            @staticmethod
            def get_available_centers():
                return RegionMedCenter.objects.values_list('med_center', flat=True).distinct()
        
        return Manager()
    
    @staticmethod
    def get_available_centers():
        return RegionMedCenter.objects.values_list('med_center', flat=True).distinct()

class DateOfBirthCompatibility:
    def __init__(self, user):
        self.user = user
        self.date_of_birth = user.date_of_birth
        self.id = user.id
    
    def age(self):
        return self.user.age()
    
    def save(self, *args, **kwargs):
        self.user.save()
    
    @classmethod
    def objects(cls):
        class Manager:
            @staticmethod
            def get_or_create(user):
                return DateOfBirthCompatibility(user), False
            
            @staticmethod
            def get(user):
                return DateOfBirthCompatibility(user)
        
        return Manager()
    
    class DoesNotExist(Exception):
        pass

class UserGenderCompatibility:
    def __init__(self, user):
        self.user = user
        self.gender = user.gender
        self.id = user.id
    
    def save(self, *args, **kwargs):
        self.user.save()
    
    @classmethod
    def objects(cls):
        class Manager:
            @staticmethod
            def get_or_create(user):
                return UserGenderCompatibility(user), False
        
        return Manager()
    
    class DoesNotExist(Exception):
        pass

class UserDescCompatibility:
    def __init__(self, user):
        self.user = user
        self.desc = user.description
        self.id = user.id
    
    def save(self, *args, **kwargs):
        self.user.save()
    
    @classmethod
    def objects(cls):
        class Manager:
            @staticmethod
            def get_or_create(user):
                return UserDescCompatibility(user), False
        
        return Manager()

class UserRoleCompatibility:
    def __init__(self, user):
        self.user = user
        self.role = user.role
        self.id = user.id
    
    def save(self, *args, **kwargs):
        self.user.save()
    
    def get_role_display(self):
        role_dict = dict(ROLE_CHOICES)
        return role_dict.get(self.role, self.role)
    
    @classmethod
    def objects(cls):
        class Manager:
            @staticmethod
            def get_or_create(user):
                return UserRoleCompatibility(user), False
            
            @staticmethod
            def filter(user):
                class QuerySet:
                    def __init__(self, user_role):
                        self.user_role = user_role
                    
                    def first(self):
                        return self.user_role
                
                return QuerySet(UserRoleCompatibility(user))
        
        return Manager()
    
    # Constants for backward compatibility
    ADMIN = 'ADMIN'
    TRAINER = 'TRAINER'
    MANAGER = 'MANAGER'
    USER = 'USER'

class Choices(models.Model):
    choice = models.CharField(max_length=5000)
    is_answer = models.BooleanField(default=False)
    scores = models.IntegerField(blank=True, default=0)    

class Questions(models.Model):
    question = models.CharField(max_length=10000)
    question_type = models.CharField(max_length=20)
    required = models.BooleanField(default=False)
    answer_key = models.CharField(max_length=5000, blank=True)
    score = models.IntegerField(blank=True, default=0)
    feedback = models.CharField(max_length=5000, null=True)
    choices = models.ManyToManyField(Choices, related_name="choices")
    max_value = models.IntegerField(blank=True, null=True, default=1)
    is_list = models.BooleanField(default=False)
    is_skip = models.BooleanField(default=False)
    is_negative = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

class Answer(models.Model):
    answer = models.CharField(max_length=5000, null=True, blank=True)  
    answer_to = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name="answer_to")
    is_skipped = models.BooleanField(default=False)

class Form(models.Model):
    code = models.CharField(max_length=30)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=10000, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator")
    background_color = models.CharField(max_length=20, default="#FEFEFE")
    text_color = models.CharField(max_length=20, default="#272124")
    collect_email = models.BooleanField(default=False)
    authenticated_responder = models.BooleanField(default=False)
    edit_after_submit = models.BooleanField(default=False)
    limit_ip = models.BooleanField(default=False)
    submit_limit = models.BooleanField(default=False)
    confirmation_message = models.CharField(max_length=10000, default="Ваш ответ был отправлен.")
    # is_quiz = models.BooleanField(default=False)
    # allow_view_score = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    is_single_form = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    allow_med_center_choice = models.BooleanField(default=False)
    updatedAt = models.DateTimeField(auto_now=True)
    questions = models.ManyToManyField(Questions, related_name="questions")

    def is_creator(self, user):
        return self.creator == user

class Responses(models.Model):
    response_code = models.CharField(max_length=20, db_index=True)
    response_to = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="response_to", db_index=True)
    responder_ip = models.CharField(max_length=30)
    responder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="responder", blank=True, null=True, db_index=True)
    responder_email = models.EmailField(blank=True)
    authenticated_responder = models.BooleanField(default=False)
    response = models.ManyToManyField(Answer, related_name="response")
    
    # Статические данные с индексами
    responder_gender = models.CharField(max_length=1, blank=True, null=True, db_index=True)
    responder_birth_date = models.DateField(blank=True, null=True)
    responder_age = models.IntegerField(blank=True, null=True, db_index=True)
    responder_city = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    responder_med = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    responder_username = models.CharField(max_length=150, blank=True, null=True, db_index=True)
    
    createdAt = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['response_to', 'responder_med']),
            models.Index(fields=['response_to', 'responder_city']),
            models.Index(fields=['response_to', 'responder_gender']),
            models.Index(fields=['response_to', 'createdAt']),
            models.Index(fields=['response_to', 'responder_username']),
        ]

    def save(self, *args, **kwargs):
        if self.response_to.authenticated_responder:
            self.authenticated_responder = True
        else:
            self.authenticated_responder = False

        if self.responder:
            # Если имя пользователя не установлено вручную, используем имя из профиля
            if not self.responder_username:
                self.responder_username = self.responder.username
                
            if not self.responder_email:
                self.responder_email = self.responder.email
            
            # Используем прямые поля пользователя вместо вложенных моделей
            if not self.responder_gender and self.responder.gender:
                self.responder_gender = self.responder.gender
            
            if not self.responder_birth_date and self.responder.date_of_birth:
                self.responder_birth_date = self.responder.date_of_birth
                self.responder_age = self.responder.age()
            
            if not self.responder_city and self.responder.city:
                self.responder_city = self.responder.city
            
            if not self.responder_med and self.responder.med_center:
                self.responder_med = self.responder.med_center
        
        super().save(*args, **kwargs)

    def get_city_display(self):
        """Возвращает отображаемое название города"""
        city_dict = dict(CITY_CHOICES)
        return city_dict.get(self.responder_city, self.responder_city)

    def get_gender_display(self):
        """Возвращает отображаемое название пола"""
        gender_dict = {
            'M': 'Мужской',
            'F': 'Женский',
            'O': 'Другой'
        }
        return gender_dict.get(self.responder_gender, self.responder_gender)





