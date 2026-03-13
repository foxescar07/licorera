from django.shortcuts import render

# Create your views here.
def proveedor(request):
    return render(request, 'proveedor.html')