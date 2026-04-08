from django.shortcuts import render
from ventas.models import Venta, DetalleVenta
from producto.models import Producto, Inventario
from proveedores.models import Proveedor

def reportes(request):
    ventas      = Venta.objects.prefetch_related('detalles__producto').all()
    productos   = Producto.objects.all().order_by('nombre')
    proveedores = Proveedor.objects.all().order_by('nombre_empresa')  # ← corregido

    total_ventas    = sum(v.total() for v in ventas)
    total_productos = sum(det.cantidad for v in ventas for det in v.detalles.all())
    total_clientes  = ventas.values('cliente').distinct().count()

    total_registrados = productos.count()
    total_en_stock    = productos.filter(cantidad_disponible__gt=10).count()
    total_stock_bajo  = productos.filter(cantidad_disponible__gt=0, cantidad_disponible__lte=10).count()
    total_agotados    = productos.filter(cantidad_disponible=0).count()

    entradas = Inventario.objects.filter(tipo='entrada').select_related('producto').order_by('-fecha_actualizada')
    salidas  = Inventario.objects.filter(tipo='salida').select_related('producto').order_by('-fecha_actualizada')

    return render(request, 'reportes.html', {
        'ventas':            ventas,
        'total_ventas':      total_ventas,
        'total_productos':   total_productos,
        'total_clientes':    total_clientes,
        'productos':         productos,
        'proveedores':       proveedores,
        'total_registrados': total_registrados,
        'total_en_stock':    total_en_stock,
        'total_stock_bajo':  total_stock_bajo,
        'total_agotados':    total_agotados,
        'entradas':          entradas,
        'salidas':           salidas,
    })