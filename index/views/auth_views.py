from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from index.models import User, CITY_CHOICES, RegionMedCenter
import re
from django.shortcuts import render
from django.http import JsonResponse
import logging
from django.contrib.auth.password_validation import validate_password as django_validate_password
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.cache import cache
from django.utils import timezone
import time

# Setup logging
logger = logging.getLogger(__name__)

# Rate limiting settings
MAX_LOGIN_ATTEMPTS = 5
LOGIN_TIMEOUT_MINUTES = 15

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def check_login_attempts(request, username):
    """Check if user has exceeded maximum login attempts"""
    ip = get_client_ip(request)
    cache_key = f"login_attempts:{username}:{ip}"
    attempts = cache.get(cache_key, 0)
    
    if attempts >= MAX_LOGIN_ATTEMPTS:
        return False
    return True

def increment_login_attempts(request, username):
    """Increment login attempts counter"""
    ip = get_client_ip(request)
    cache_key = f"login_attempts:{username}:{ip}"
    attempts = cache.get(cache_key, 0)
    attempts += 1
    
    # Set timeout for login attempts
    timeout = LOGIN_TIMEOUT_MINUTES * 60
    cache.set(cache_key, attempts, timeout)
    
    return attempts

def reset_login_attempts(request, username):
    """Reset login attempts counter"""
    ip = get_client_ip(request)
    cache_key = f"login_attempts:{username}:{ip}"
    cache.delete(cache_key)

@ensure_csrf_cookie
def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    
    if request.method == "POST":
        username = request.POST["username"].lower()
        password = request.POST["password"]
        
        # Check if user has exceeded maximum login attempts
        if not check_login_attempts(request, username):
            logger.warning(f"Login blocked due to too many attempts for user: {username} from IP: {get_client_ip(request)}")
            return render(request, "registration/loginregister.html", {
                "message": f"Слишком много попыток входа. Пожалуйста, попробуйте снова через {LOGIN_TIMEOUT_MINUTES} минут.",
                "city_choices": CITY_CHOICES
            })
        
        # Add a small delay to prevent timing attacks
        time.sleep(0.1)
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Log successful login
            logger.info(f"Successful login for user: {username}")
            # Reset login attempts
            reset_login_attempts(request, username)
            return HttpResponseRedirect(reverse('index'))
        else:
            # Increment login attempts
            attempts = increment_login_attempts(request, username)
            remaining_attempts = MAX_LOGIN_ATTEMPTS - attempts
            
            # Log failed login attempt
            logger.warning(f"Failed login attempt for username: {username}, attempts: {attempts}")
            
            message = "Неверное имя пользователя или пароль."
            if remaining_attempts > 0:
                message += f" Осталось попыток: {remaining_attempts}"
            
            return render(request, "registration/loginregister.html", {
                "message": message,
                "city_choices": CITY_CHOICES
            })
    return render(request, "registration/loginregister.html", {
        "city_choices": CITY_CHOICES
    })

@ensure_csrf_cookie
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

        # Validate all required fields are provided
        if not all([username, password, email, confirmation, region, med_center]):
            return render(request, "registration/loginregister.html", {
                "message": "Все поля обязательны для заполнения.",
                "city_choices": CITY_CHOICES
            })

        # Validate username format
        if not re.match(r'^[a-zA-Z0-9]+$', username):
            return render(request, "registration/loginregister.html", {
                "message": "Имя пользователя может содержать только латинские буквы и цифры.",
                "city_choices": CITY_CHOICES
            })

        # Validate username length
        if len(username) < 4 or len(username) > 30:
            return render(request, "registration/loginregister.html", {
                "message": "Имя пользователя должно содержать от 4 до 30 символов.",
                "city_choices": CITY_CHOICES
            })

        # Validate email format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return render(request, "registration/loginregister.html", {
                "message": "Пожалуйста, введите корректный email адрес.",
                "city_choices": CITY_CHOICES
            })

        # Validate password strength
        error_message = validate_password(password, confirmation)
        if error_message:
            return render(request, "registration/loginregister.html", {
                "message": error_message,
                "city_choices": CITY_CHOICES
            })

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return render(request, "registration/loginregister.html", {
                "message": "Email уже занят.",
                "city_choices": CITY_CHOICES
            })

        # Validate region exists
        if not any(region == code for code, _ in CITY_CHOICES):
            return render(request, "registration/loginregister.html", {
                "message": "Выбран недопустимый регион.",
                "city_choices": CITY_CHOICES
            })

        # Validate med_center exists for the selected region
        if not RegionMedCenter.objects.filter(region=region, med_center=med_center).exists():
            return render(request, "registration/loginregister.html", {
                "message": "Выбран недопустимый медицинский центр для данного региона.",
                "city_choices": CITY_CHOICES
            })

        try:
            # Create user with all fields at once
            user = User.objects.create_user(
                username=username, 
                password=password, 
                email=email,
                city=region,
                med_center=med_center
            )
            
            # Log successful registration
            logger.info(f"New user registered: {username}")
            
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        except IntegrityError:
            return render(request, "registration/loginregister.html", {
                "message": "Имя пользователя уже занято",
                "city_choices": CITY_CHOICES
            })
    
    # For GET request, pass the list of cities
    return render(request, "registration/loginregister.html", {
        'city_choices': CITY_CHOICES,
    })

def validate_password(password, confirmation):
    if password != confirmation:
        return "Пароли должны совпадать."
    
    # Basic password requirements
    if len(password) < 8:
        return "Пароль должен содержать как минимум 8 символов."
    
    if not any(char.isdigit() for char in password):
        return "Пароль должен содержать хотя бы одну цифру."
    
    if not any(char.isupper() for char in password):
        return "Пароль должен содержать хотя бы одну заглавную букву."
    
    if not any(char.islower() for char in password):
        return "Пароль должен содержать хотя бы одну строчную букву."
    
    if not any(char in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for char in password):
        return "Пароль должен содержать хотя бы один специальный символ."
    
    # Check for common passwords
    common_passwords = ["password", "12345678", "qwerty", "admin123", "letmein", "welcome"]
    if password.lower() in common_passwords:
        return "Пароль слишком распространен и легко угадывается."
    
    # Try Django's built-in password validation
    try:
        django_validate_password(password)
    except ValidationError as e:
        return e.messages[0]
    
    return None

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def get_med_centers(request):
    """API endpoint to get medical centers for a specific region"""
    region = request.GET.get('region')
    if not region:
        return JsonResponse([], safe=False)
        
    med_centers = RegionMedCenter.objects.filter(region=region).values('med_center', 'address')
    return JsonResponse(list(med_centers), safe=False)