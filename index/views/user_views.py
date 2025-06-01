from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from index.models import User, Image, RegionMedCenter, CITY_CHOICES, ROLE_CHOICES
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.core.files.base import ContentFile

@login_required
def update_user_status(request, user_id):
    # Только администраторы могут менять роли
    if not request.user.is_admin():
        return HttpResponseForbidden("Только администраторы могут менять роли пользователей")

    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        role = request.POST.get('role')
        
        # Проверяем, что роль допустима
        valid_roles = [choice[0] for choice in ROLE_CHOICES]
        if role in valid_roles:
            # Обновляем роль пользователя напрямую
            user.role = role
            
            # Обновляем статус суперпользователя и персонала
            if role == 'ADMIN':
                user.is_superuser = True
                user.is_staff = True
            elif role in ['TRAINER', 'MANAGER']:
                user.is_superuser = False
                user.is_staff = True
            else:
                user.is_superuser = False
                user.is_staff = False
            
            user.save()
        
        return redirect(reverse('user_detail', args=[user.id]))

    return render(request, 'index/user/user_detail.html', {
        'user': user,
        'current_role': user.role
    })


def change_desc(request):
    if request.method == 'POST':
        new_desc = request.POST.get('desc')  
        request.user.description = new_desc
        request.user.save()

        return redirect('edit_profile')  

    context = {}
    return render(request, 'index/user/user_profile.html', context)


def change_date_of_birth(request):
    if request.method == 'POST':
        new_date_of_birth = request.POST.get('date_of_birth', None)
        request.user.date_of_birth = new_date_of_birth
        request.user.save()
        return redirect('edit_profile')

    context = {'user': request.user}
    return render(request, 'index/user/user_profile.html', context)

def delete_date_of_birth(request):
    request.user.date_of_birth = None
    request.user.save()
    return redirect('edit_profile')

@login_required
def change_gender(request):
    if request.method == 'POST':
        new_gender = request.POST.get('gender', 'O')
        request.user.gender = new_gender
        request.user.save()
        return redirect('edit_profile')

    context = {'user': request.user}
    return render(request, 'index/user/user_profile.html', context)

@login_required
def change_username(request):
    if request.method == 'POST':
        new_username = request.POST.get('username')
        if new_username:
            request.user.username = new_username
            request.user.save()
            messages.success(request, 'Username успешно изменен.')
        else:
            messages.error(request, 'Пожалуйста, введите новый username.')

    return redirect('edit_profile')

@login_required
def change_email(request):
    if request.method == 'POST':
        new_email = request.POST.get('email')
        if new_email:
            request.user.email = new_email
            request.user.save()
            messages.success(request, 'Email успешно изменен.')
        else:
            messages.error(request, 'Пожалуйста, введите новый email.')

    return redirect('edit_profile')

def change_profile_image(request):
    if request.method == 'POST':
        image_file = request.FILES.get('imageFile')
        if image_file:
            # Удаляем старое изображение, если оно существует
            old_image = Image.objects.filter(user=request.user).first()
            if old_image:
                old_image.delete()

            # Сохраняем новое изображение
            image = Image(user=request.user)
            image.image.save(image_file.name, ContentFile(image_file.read()))
            image.save()

    return redirect('edit_profile')

def delete_profile_image(request):
    if request.method == 'POST':
        image = Image.objects.filter(user=request.user).first()
        if image:
            image.delete()
    return redirect('edit_profile')

def delete_users(request):
    if request.method == 'POST':
        selected_users = request.POST.getlist('selected_users[]')
        if selected_users:
            User.objects.filter(id__in=selected_users).delete()
            messages.success(request, 'Пользователи успешно удалены.')
        return redirect('user_list')


def user_list(request):
    users = User.objects.all()
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    return render(request, 'index/user/user_list.html', {'users': users})

def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    context = {
        'city_choices': CITY_CHOICES,
        'med_centers': RegionMedCenter.objects.all().order_by('region', 'med_center'),
        'user': user
    }
    return render(request, 'index/user/user_detail.html', context)


def edit_profile(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    if request.method == 'POST':
        new_city = request.POST.get('City')
        if new_city is not None:
            request.user.city = new_city
            request.user.save()
            return redirect('edit_profile')

    context = {
        'city_choices': CITY_CHOICES
    }
    return render(request, 'index/user/user_profile.html', context)

def view_profile(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    return render(request, 'index/user/user_profile.html')