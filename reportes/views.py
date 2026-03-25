from django.shortcuts import render

def login_proyecto(request):
    return render(request, 'login.html')