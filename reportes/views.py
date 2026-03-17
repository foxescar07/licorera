from django.shortcuts import render
def reporte(request):
  return render(request, 'reportes/reporte.html')