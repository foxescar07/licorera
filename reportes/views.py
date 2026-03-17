from django.shortcuts import render

# El nombre DEBE ser 'reporte' para que coincida con views.reporte
def reporte(request):
    return render(request, 'reportes.html')