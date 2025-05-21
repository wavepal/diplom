from django.shortcuts import render

def FourZeroThree(request, exception=None):
    return render(request, 'error/403.html', status=403)

def FourZeroFour(request, exception=None):
    return render(request, 'error/404.html', status=404)