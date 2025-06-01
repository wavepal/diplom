from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from index.models import User, RegionMedCenter, MedCenterGroup, CITY_CHOICES
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404

@login_required
def add_medical_center(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
        
    default_group_id = request.GET.get('group')
    
    if request.method == "POST":
        region = request.POST.get('region')
        med_center = request.POST.get('med_center')
        address = request.POST.get('address')
        group_id = request.POST.get('group')
        
        if region and med_center and address:
            group = None
            if group_id:
                group = get_object_or_404(MedCenterGroup, id=group_id)
                
            RegionMedCenter.objects.create(
                region=region,
                med_center=med_center,
                address=address,
                group=group
            )
            messages.success(request, "Медицинский центр успешно добавлен")
            
            if group:
                return HttpResponseRedirect(reverse("group_medical_centers", args=[group.id]))
            return HttpResponseRedirect(reverse("manage_medical_centers"))
            
    return render(request, "index/medcenters/add_edit_medical_center.html", {
        "city_choices": CITY_CHOICES,
        "med_center_groups": MedCenterGroup.objects.all(),
        "default_group_id": default_group_id
    })

@login_required
def get_med_centers(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
    
    region = request.GET.get('region')
    med_centers = RegionMedCenter.objects.filter(region=region).values('med_center', 'address')
    return JsonResponse(list(med_centers), safe=False)

@login_required
def edit_medical_center(request, center_id):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
        
    center = get_object_or_404(RegionMedCenter, id=center_id)
    return_to_group = request.GET.get('group')
    
    if request.method == "POST":
        region = request.POST.get('region')
        med_center = request.POST.get('med_center')
        address = request.POST.get('address')
        group_id = request.POST.get('group')
        
        if region and med_center:
            center.region = region
            center.med_center = med_center
            center.address = address
            
            if group_id:
                center.group = get_object_or_404(MedCenterGroup, id=group_id)
            else:
                center.group = None
                
            center.save()
            messages.success(request, "Медицинский центр успешно обновлен")
            
            if return_to_group:
                return HttpResponseRedirect(reverse("group_medical_centers", args=[return_to_group]))
            return HttpResponseRedirect(reverse("manage_medical_centers"))
            
    return render(request, "index/medcenters/add_edit_medical_center.html", {
        "center": center,
        "city_choices": CITY_CHOICES,
        "med_center_groups": MedCenterGroup.objects.all(),
        "default_group_id": return_to_group
    })

@login_required
def manage_medical_centers(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
        
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'add':
            region = request.POST.get('region')
            med_center = request.POST.get('med_center')
            address = request.POST.get('address')
            
            if region and med_center:
                RegionMedCenter.objects.create(
                    region=region,
                    med_center=med_center,
                    address=address or ''
                )
                messages.success(request, "Медицинский центр успешно добавлен")
                
        elif action == 'edit':
            center_id = request.POST.get('center_id')
            region = request.POST.get('region')
            med_center = request.POST.get('med_center')
            address = request.POST.get('address')
            
            if center_id:
                center = get_object_or_404(RegionMedCenter, id=center_id)
                center.region = region
                center.med_center = med_center
                center.address = address
                center.save()
                messages.success(request, "Медицинский центр успешно обновлен")
                
        elif action == 'delete':
            center_id = request.POST.get('center_id')
            if center_id:
                RegionMedCenter.objects.filter(id=center_id).delete()
                messages.success(request, "Медицинский центр успешно удален")
                return JsonResponse({'status': 'success'})
                
        elif action == 'delete_group':
            group_id = request.POST.get('group_id')
            if group_id:
                group = get_object_or_404(MedCenterGroup, id=group_id)
                # Удаляем группу, но оставляем медцентры
                RegionMedCenter.objects.filter(group=group).update(group=None)
                group.delete()
                messages.success(request, "Группа медицинских центров успешно удалена")
                return JsonResponse({'status': 'success'})
                
    med_centers = RegionMedCenter.objects.all().order_by('region', 'med_center')
    med_center_groups = MedCenterGroup.objects.all().order_by('name')
    
    return render(request, "index/medcenters/manage_medical_centers.html", {
        "med_centers": med_centers,
        "med_center_groups": med_center_groups,
        "city_choices": CITY_CHOICES
    })

@login_required
def update_med_center(request, user_id):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
        
    user = get_object_or_404(User, id=user_id)
    med_centers = RegionMedCenter.objects.all().order_by('region', 'med_center')

    if request.method == 'POST':
        med_center_name = request.POST.get('med_center')
        if med_center_name:
            # Обновляем медцентр пользователя напрямую
            user.med_center = med_center_name
            user.save()
            
            messages.success(request, f"Медицинский центр для {user.username} был обновлен!")
            return redirect('update_med_center', user_id=user.id)
        else:
            messages.error(request, "Пожалуйста, выберите медицинский центр.")
    
    return render(request, 'index/medcenters/manage_medical_centers.html', {
        'user': user,
        'med_centers': med_centers,
    })