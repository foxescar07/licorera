from django.shortcuts import render


def home(request):
        nombre = 'cristian'
        context = {
        'nombre': nombre,
        'titulo': 'Home'
    }
        return render(request, 'home.html', context)