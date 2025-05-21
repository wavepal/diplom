from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from index.models import RegionMedCenter, User, DateOfBirth, UserGender, Image, UserDesc, UserCity, UserMed, UserRole
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
        
        # Получаем или создаем объект роли для пользователя
        user_role, created = UserRole.objects.get_or_create(user=user)
        
        # Обновляем роль в зависимости от выбора
        if role in [UserRole.ADMIN, UserRole.TRAINER, UserRole.MANAGER, UserRole.USER]:
            user_role.role = role
            user_role.save()
            
            # Обновляем статус суперпользователя и персонала
            if role == UserRole.ADMIN:
                user.is_superuser = True
                user.is_staff = True
            elif role in [UserRole.TRAINER, UserRole.MANAGER]:
                user.is_superuser = False
                user.is_staff = True
            else:
                user.is_superuser = False
                user.is_staff = False
            
            user.save()
        
        return redirect(reverse('user_detail', args=[user.id]))

    # Получаем текущую роль пользователя для отображения в форме
    current_role = UserRole.objects.filter(user=user).first()
    
    return render(request, 'index/user_detail.html', {
        'user': user,
        'current_role': current_role.role if current_role else UserRole.USER
    })


def change_desc(request):
    if request.method == 'POST':
        new_desc = request.POST.get('desc')  
        user_desc, created = UserDesc.objects.get_or_create(user=request.user)
        user_desc.desc = new_desc
        user_desc.save()

        return redirect('edit_profile')  

    context = {}
    return render(request, 'index/edit-profile.html', context)


def change_date_of_birth(request):
    try:
        user_date_of_birth = request.user.dateofbirth
    except DateOfBirth.DoesNotExist:
        user_date_of_birth = DateOfBirth(user=request.user, date_of_birth=None)
        user_date_of_birth.save()

    try:
        if request.method == 'POST':
            new_date_of_birth = request.POST.get('date_of_birth', None)

            if request.user.dateofbirth.id != user_date_of_birth.id:
                return HttpResponseForbidden("You do not have permission to perform this action.")

            user_date_of_birth.date_of_birth = new_date_of_birth
            user_date_of_birth.save()
            return redirect('edit_profile')

    except Exception as e:
        print(f"An error occurred: {e}")
        return redirect('404') 

    context = {'user': request.user}
    return render(request, 'index/edit-profile.html', context)

def delete_date_of_birth(request):
    user = request.user
    try:
        user_date_of_birth = DateOfBirth.objects.get(user=user)
        user_date_of_birth.delete()
        return redirect('edit_profile')
    except DateOfBirth.DoesNotExist:
        return HttpResponse("Date of Birth not found", status=404)

@login_required
def change_gender(request):
    # Проверяем, имеет ли пользователь профиль с гендером
    try:
        user_gender = request.user.usergender
    except UserGender.DoesNotExist:

        user_gender = UserGender(user=request.user, gender='O')
        user_gender.save()

    if request.method == 'POST':

        new_gender = request.POST.get('gender', 'O')

        if request.user.usergender.id != user_gender.id:
            return HttpResponseForbidden("You do not have permission to perform this action.")

        user_gender.gender = new_gender
        user_gender.save()
        return redirect('edit_profile')

    context = {'user': request.user}
    return render(request, 'index/edit-profile.html', context)

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
    return render(request, 'index/user-list.html', {'users': users})

def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    context = {
        'user_city': UserCity.objects.get_or_create(user=user)[0],
        'user_med': UserMed.objects.get_or_create(user=user)[0],
        'city_choices': UserCity.CITY_CHOICES,
        'med_centers': RegionMedCenter.objects.all().order_by('region', 'med_center'),
        'user': user
    }
    return render(request, 'index/user_detail.html', context)


def edit_profile(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    if request.method == 'POST':
        new_city = request.POST.get('City')
        if new_city is not None:
            user_city, created = UserCity.objects.get_or_create(user=request.user)
            user_city.city = new_city
            user_city.save()
            return redirect('edit_profile')

    context = {
        'user_city': UserCity.objects.get_or_create(user=request.user)[0],
        'user_med': UserMed.objects.get_or_create(user=request.user)[0],
        'city_choices': UserCity.CITY_CHOICES
    }
    return render(request, 'index/edit-profile.html', context)

def view_profile(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    return render(request, 'index/view-profile.html')