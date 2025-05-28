from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
import os
from django.utils import timezone

class UserCity(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name='city_info')
    ASTANA = 'ASTANA'
    ALMATY = 'ALMATY'
    AKTOBE = 'AKTOBE'
    ATYRAUSKAYA = 'ATYRAUSKAYA'
    ZAPADNO = 'ZAPADNO'
    KYZYLORDA = 'KYZYLORDA'
    MANGISTAU = 'MANGISTAU'
    PAVLODAR = 'PAVLODAR'
    TURKESTAN = 'TURKESTAN'

    CITY_CHOICES = [
        (ASTANA, 'Астана'),
        (ALMATY, 'Алматы'),
        (AKTOBE, 'Актюбинская область'),
        (ATYRAUSKAYA, 'Атырауская область'),
        (ZAPADNO, 'Западно-Казахстанская область'),
        (KYZYLORDA, 'Кызылординская область'),
        (MANGISTAU, 'Мангистауская область'),
        (PAVLODAR, 'Павлодарская область'),
        (TURKESTAN, 'Южно-Казахстанская область'),
    ]

    city = models.CharField(max_length=50, blank=True, null=True, choices=CITY_CHOICES)

class DateOfBirth(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name='date_info')
    date_of_birth = models.DateField(blank=True, null=True)

    def age(self):
        today = datetime.now().date()
        birthdate = self.date_of_birth
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        return age

    def __str__(self):
        return f"{self.user.username}'s Date of Birth"

class UserGender(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name='gender_info')
    gender_choices = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=gender_choices)

    def __str__(self):
        return f"{self.user.username}'s Gender"

class Image(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name='image_info')
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def delete(self, *args, **kwargs):
        # Удаляем файл изображения при удалении объекта
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super(Image, self).delete(*args, **kwargs)

class UserDesc(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name='desc_info')
    desc = models.CharField(max_length=256, blank=True, null=True)

class UserMed(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name="med_info")
    med_center = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Medical Center"

    @classmethod
    def get_available_centers(cls):
        return RegionMedCenter.objects.values_list('med_center', flat=True).distinct()

class MedCenterGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class RegionMedCenter(models.Model):
    region = models.CharField(max_length=50, choices=UserCity.CITY_CHOICES)
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

class UserRole(models.Model):
    ADMIN = 'ADMIN'
    TRAINER = 'TRAINER'
    MANAGER = 'MANAGER'
    USER = 'USER'

    ROLE_CHOICES = [
        (ADMIN, 'Администратор'),
        (TRAINER, 'Тренер'),
        (MANAGER, 'Руководитель'),
        (USER, 'Пользователь'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=USER)
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name='role_info')

    def __str__(self):
        return f"{self.user.username}'s Role: {self.get_role_display()}"

    class Meta:
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователей'

class User(AbstractUser):
    date_of_birth = models.ForeignKey(DateOfBirth, on_delete=models.CASCADE, null=True, blank=True, related_name='user_info')
    gender = models.ForeignKey(UserGender, on_delete=models.CASCADE, null=True, blank=True, related_name='user_info')
    image = models.ForeignKey(Image, on_delete=models.CASCADE, null=True, blank=True, related_name='user_info')
    desc = models.ForeignKey(UserDesc, on_delete=models.CASCADE, null=True, blank=True, related_name='user_info')
    city = models.ForeignKey(UserCity, on_delete=models.CASCADE, null=True, blank=True, related_name='user_info')
    med_center = models.ForeignKey(UserMed, on_delete=models.CASCADE, null=True, blank=True, related_name='user_info')

    @property
    def role(self):
        try:
            return self.role_info.role
        except UserRole.DoesNotExist:
            return UserRole.USER

    def is_admin(self):
        return self.role == UserRole.ADMIN

    def is_trainer(self):
        return self.role == UserRole.TRAINER

    def is_manager(self):
        return self.role == UserRole.MANAGER

    def is_regular_user(self):
        return self.role == UserRole.USER

class Choices(models.Model):
    choice = models.CharField(max_length=5000)
    is_answer = models.BooleanField(default=False)
    scores = models.IntegerField(blank = True, default=0)    

class Questions(models.Model):
    question = models.CharField(max_length= 10000)
    question_type = models.CharField(max_length=20)
    required = models.BooleanField(default= False)
    answer_key = models.CharField(max_length = 5000, blank = True)
    score = models.IntegerField(blank = True, default=0)
    feedback = models.CharField(max_length = 5000, null = True)
    choices = models.ManyToManyField(Choices, related_name = "choices")
    max_value = models.IntegerField(blank = True, null=True, default=1)
    is_list = models.BooleanField(default= False)
    is_skip = models.BooleanField(default= False)
    is_negative = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

class Answer(models.Model):
    answer = models.CharField(max_length=5000, null=True, blank=True)  
    answer_to = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name="answer_to")
    is_skipped = models.BooleanField(default= False)

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
    is_quiz = models.BooleanField(default=False)
    allow_view_score = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    is_single_form = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
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
    
    # Добавляем новые поля для статических данных с индексами
    responder_gender = models.CharField(max_length=1, blank=True, null=True, db_index=True)
    responder_birth_date = models.DateField(blank=True, null=True)
    responder_age = models.IntegerField(blank=True, null=True, db_index=True)
    responder_city = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    responder_med = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    responder_username = models.CharField(max_length=150, blank=True, null=True)
    
    createdAt = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['response_to', 'responder_med']),
            models.Index(fields=['response_to', 'responder_city']),
            models.Index(fields=['response_to', 'responder_gender']),
            models.Index(fields=['response_to', 'createdAt']),
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
            
            # Остальная логика остается без изменений
            if hasattr(self.responder, 'gender_info') and not self.responder_gender:
                self.responder_gender = self.responder.gender_info.gender
            
            if hasattr(self.responder, 'date_info') and not self.responder_birth_date:
                self.responder_birth_date = self.responder.date_info.date_of_birth
                self.responder_age = self.responder.date_info.age()
            
            if hasattr(self.responder, 'city_info') and not self.responder_city:
                self.responder_city = self.responder.city_info.city
            
            if hasattr(self.responder, 'med_info') and not self.responder_med:
                self.responder_med = self.responder.med_info.med_center
        
        super().save(*args, **kwargs)

    def get_city_display(self):
        """Возвращает отображаемое название города"""
        city_dict = dict(UserCity.CITY_CHOICES)
        return city_dict.get(self.responder_city, self.responder_city)

    def get_gender_display(self):
        """Возвращает отображаемое название пола"""
        gender_dict = {
            'M': 'Мужской',
            'F': 'Женский',
            'O': 'Другой'
        }
        return gender_dict.get(self.responder_gender, self.responder_gender)





