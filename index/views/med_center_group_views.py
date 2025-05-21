from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from index.models import MedCenterGroup, RegionMedCenter

@login_required
def add_med_center_group(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
        
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if name:
            MedCenterGroup.objects.create(
                name=name,
                description=description
            )
            messages.success(request, "Группа медицинских центров успешно создана")
            return HttpResponseRedirect(reverse("manage_medical_centers"))
            
    return render(request, "index/add_edit_med_center_group.html")

@login_required
def edit_med_center_group(request, group_id):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
        
    group = get_object_or_404(MedCenterGroup, id=group_id)
    
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if name:
            group.name = name
            group.description = description
            group.save()
            messages.success(request, "Группа медицинских центров успешно обновлена")
            return HttpResponseRedirect(reverse("manage_medical_centers"))
            
    return render(request, "index/add_edit_med_center_group.html", {
        "group": group
    })

@login_required
def group_medical_centers(request, group_id):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
        
    group = get_object_or_404(MedCenterGroup, id=group_id)
    med_centers = RegionMedCenter.objects.filter(group=group)
    
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'delete':
            center_id = request.POST.get('center_id')
            if center_id:
                RegionMedCenter.objects.filter(id=center_id).delete()
                messages.success(request, "Медицинский центр успешно удален")
                return JsonResponse({'status': 'success'})
                
    return render(request, "index/group_medical_centers.html", {
        "group": group,
        "med_centers": med_centers
    }) 