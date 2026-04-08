from django.shortcuts import render
from ventas.models import Venta, DetalleVenta

def reportes(request):
    ventas = Venta.objects.prefetch_related('detalles__producto').all()

    total_ventas    = sum(v.total() for v in ventas)
    total_productos = sum(det.cantidad for v in ventas for det in v.detalles.all())
    total_clientes  = ventas.values('cliente').distinct().count()

    return render(request, 'reportes.html', {
        'ventas':          ventas,
        'total_ventas':    total_ventas,
        'total_productos': total_productos,
        'total_clientes':  total_clientes,
    })