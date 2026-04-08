from django.shortcuts import render
from ventas.models import Venta, DetalleVenta
from producto.models import Producto

def reportes(request):
    ventas   = Venta.objects.prefetch_related('detalles__producto').all()
    productos = Producto.objects.all().order_by('nombre')

    total_ventas    = sum(v.total() for v in ventas)
    total_productos = sum(det.cantidad for v in ventas for det in v.detalles.all())
    total_clientes  = ventas.values('cliente').distinct().count()

    # Conteos para las tarjetas del modal
    total_registrados = productos.count()
    total_en_stock    = productos.filter(cantidad_disponible__gt=10).count()
    total_stock_bajo  = productos.filter(cantidad_disponible__gt=0, cantidad_disponible__lte=10).count()
    total_agotados    = productos.filter(cantidad_disponible=0).count()

    return render(request, 'reportes.html', {
        'ventas':             ventas,
        'total_ventas':       total_ventas,
        'total_productos':    total_productos,
        'total_clientes':     total_clientes,
        'productos':          productos,
        'total_registrados':  total_registrados,
        'total_en_stock':     total_en_stock,
        'total_stock_bajo':   total_stock_bajo,
        'total_agotados':     total_agotados,
    })