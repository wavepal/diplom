from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from index.models import User, UserCity, UserMed
import re
from django.shortcuts import render

def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if request.method == "POST":
        username = request.POST["username"].lower()
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, "registration/loginregister.html", {
                "message": "Неверное имя пользователя или пароль.",
                "city_choices": UserCity.CITY_CHOICES  # Добавляем city_choices
            })
    return render(request, "registration/loginregister.html", {
        "city_choices": UserCity.CITY_CHOICES  # Добавляем city_choices
    })

def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    
    if request.method == "POST":
        username = request.POST["username"].lower()
        password = request.POST["password"]
        email = request.POST["email"]
        confirmation = request.POST["confirmation"]
        region = request.POST.get("region")
        med_center = request.POST.get("med_center")

        if not re.match(r'^[a-zA-Z0-9]+$', username):
            return render(request, "registration/loginregister.html", {
                "message": "Имя пользователя может содержать только латинские буквы и цифры.",
                "city_choices": UserCity.CITY_CHOICES
            })

        error_message = validate_password(password, confirmation)
        if error_message:
            return render(request, "registration/loginregister.html", {
                "message": error_message,
                "city_choices": UserCity.CITY_CHOICES
            })

        if User.objects.filter(email=email).exists():
            return render(request, "registration/loginregister.html", {
                "message": "Email уже занят.",
                "city_choices": UserCity.CITY_CHOICES
            })

        try:
            user = User.objects.create_user(username=username, password=password, email=email)
            
            # Создаем запись о городе
            user_city = UserCity.objects.create(user=user, city=region)
            
            # Создаем запись о медцентре
            UserMed.objects.create(user=user, med_center=med_center)
            
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        except IntegrityError:
            return render(request, "registration/loginregister.html", {
                "message": "Имя пользователя уже занято",
                "city_choices": UserCity.CITY_CHOICES
            })
    
    # Для GET-запроса передаем список городов
    return render(request, "registration/loginregister.html", {
        'city_choices': UserCity.CITY_CHOICES,
    })

def validate_password(password, confirmation):
    if password != confirmation:
        return "Пароли должны совпадать."
    elif len(password) < 8:
        return "Пароль должен содержать как минимум 8 символов."
    elif not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
        return "Пароль должен содержать буквы и цифры."
    return None

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))