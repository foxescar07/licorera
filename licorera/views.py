from django.shortcuts import render

def login_proyecto(request):
    # Esto simplemente abre tu página de login
    return render(request, 'login.html')