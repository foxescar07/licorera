from django.shortcuts import render
<<<<<<< Updated upstream

# El nombre DEBE ser 'reporte' para que coincida con views.reporte
=======
>>>>>>> Stashed changes
def reporte(request):
    return render(request, 'reportes/reporte.html')