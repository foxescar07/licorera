from django.shortcuts import render

# Create your views here.
def proveedores(request):
    return render(request, 'proveedores.html')