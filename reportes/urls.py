from django.shortcuts import render

<<<<<<< Updated upstream
# El nombre DEBE ser 'reporte' para que coincida con views.reporte
def reporte(request):
    return render(request, 'reportes.html')
=======
def reporte_ventas(request):
    return render(request, 'reportes/reporte.html')
>>>>>>> Stashed changes
