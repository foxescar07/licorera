from django.shortcuts import render

def login_usuario(request):
    return render(request, 'login.html') # Asegúrate de que el archivo se llame así

def registro_usuario(request):
    return render(request, 'registro.html')